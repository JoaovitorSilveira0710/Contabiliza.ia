from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text, case, and_, or_
from typing import Dict, Any, List
from datetime import datetime, date, timedelta
import logging

from ..models.database import get_db
from ..models.clientes import Cliente
from ..models.financeiro import LancamentoFinanceiro, IndicadorFinanceiro
from ..models.contabil import ObrigacaoAcessoria, DRE
from ..models.juridico import Processo, AndamentoProcessual
from ..models.notas_fiscais import NotaFiscal  # 🔥 CORREÇÃO: notas_fiscais em vez de notas

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

@router.get("/")
def get_dashboard_data(
    periodo: str = "mensal",  # mensal, trimestral, anual
    db: Session = Depends(get_db)
):
    """Retorna todos os dados para o dashboard com filtro de período"""
    
    try:
        # Métricas principais
        metrics = get_main_metrics(db, periodo)
        
        # Dados para gráficos
        charts_data = get_charts_data(db, periodo)
        
        # Atividades recentes
        recent_activities = get_recent_activities(db)
        
        # Principais clientes
        top_clients = get_top_clients(db, periodo)
        
        # Próximos vencimentos
        upcoming_deadlines = get_upcoming_deadlines(db)
        
        # Alertas e notificações
        alerts = get_alerts(db)
        
        # Performance por área
        performance_by_area = get_performance_by_area(db, periodo)
        
        return {
            "periodo": periodo,
            "metrics": metrics,
            "charts": charts_data,
            "recent_activities": recent_activities,
            "top_clients": top_clients,
            "upcoming_deadlines": upcoming_deadlines,
            "alerts": alerts,
            "performance_by_area": performance_by_area,
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Erro no dashboard: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao carregar dados do dashboard: {str(e)}"
        )

def get_main_metrics(db: Session, periodo: str = "mensal") -> Dict[str, Any]:
    """Calcula as métricas principais do dashboard"""
    
    try:
        # Definir período base
        hoje = datetime.now()
        if periodo == "mensal":
            data_inicio = date(hoje.year, hoje.month, 1)
            periodo_anterior = (data_inicio - timedelta(days=1)).replace(day=1)
        elif periodo == "trimestral":
            trimestre_atual = (hoje.month - 1) // 3 + 1
            mes_inicio_trimestre = (trimestre_atual - 1) * 3 + 1
            data_inicio = date(hoje.year, mes_inicio_trimestre, 1)
            periodo_anterior = (data_inicio - timedelta(days=90)).replace(day=1)
        else:  # anual
            data_inicio = date(hoje.year, 1, 1)
            periodo_anterior = date(hoje.year - 1, 1, 1)
        
        # Total de clientes ativos
        total_clientes = db.query(Cliente).filter(Cliente.ativo == True).count()
        
        # Faturamento do período atual
        faturamento_atual = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.tipo == "receita",
            LancamentoFinanceiro.status == "pago",
            LancamentoFinanceiro.data_pagamento >= data_inicio
        ).scalar() or 0
        
        # Faturamento do período anterior (para cálculo de variação)
        faturamento_anterior = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.tipo == "receita",
            LancamentoFinanceiro.status == "pago",
            LancamentoFinanceiro.data_pagamento >= periodo_anterior,
            LancamentoFinanceiro.data_pagamento < data_inicio
        ).scalar() or 0
        
        # Cálculo da variação percentual
        variacao_faturamento = 0
        if faturamento_anterior > 0:
            variacao_faturamento = ((faturamento_atual - faturamento_anterior) / faturamento_anterior) * 100
        
        # Obrigações pendentes
        obrigacoes_pendentes = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.status == "pendente"
        ).count()
        
        # Obrigações próximas do vencimento (próximos 7 dias)
        data_limite = date.today() + timedelta(days=7)
        obrigacoes_proximas = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.status == "pendente",
            ObrigacaoAcessoria.data_vencimento <= data_limite,
            ObrigacaoAcessoria.data_vencimento >= date.today()
        ).count()
        
        # Inadimplência (lançamentos em atraso)
        lancamentos_atrasados = db.query(LancamentoFinanceiro).filter(
            LancamentoFinanceiro.status == "atrasado",
            LancamentoFinanceiro.tipo == "receita"
        ).count()
        
        # Processos ativos
        processos_ativos = db.query(Processo).filter(
            Processo.status == "ativo"
        ).count()
        
        # Novos clientes no período
        novos_clientes = db.query(Cliente).filter(
            Cliente.ativo == True,
            Cliente.data_cadastro >= data_inicio
        ).count()
        
        # Taxa de inadimplência
        taxa_inadimplencia = 0
        if total_clientes > 0:
            taxa_inadimplencia = (lancamentos_atrasados / total_clientes) * 100
        
        return {
            "faturamento_atual": float(faturamento_atual),
            "faturamento_anterior": float(faturamento_anterior),
            "variacao_faturamento": round(variacao_faturamento, 2),
            "total_clientes": total_clientes,
            "novos_clientes": novos_clientes,
            "obrigacoes_pendentes": obrigacoes_pendentes,
            "obrigacoes_proximas": obrigacoes_proximas,
            "lancamentos_atrasados": lancamentos_atrasados,
            "processos_ativos": processos_ativos,
            "taxa_inadimplencia": round(taxa_inadimplencia, 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro nas métricas principais: {str(e)}")
        return {
            "faturamento_atual": 0,
            "faturamento_anterior": 0,
            "variacao_faturamento": 0,
            "total_clientes": 0,
            "novos_clientes": 0,
            "obrigacoes_pendentes": 0,
            "obrigacoes_proximas": 0,
            "lancamentos_atrasados": 0,
            "processos_ativos": 0,
            "taxa_inadimplencia": 0
        }

def get_charts_data(db: Session, periodo: str = "mensal") -> Dict[str, Any]:
    """Prepara dados para os gráficos do dashboard"""
    
    try:
        # Evolução de faturamento (últimos 12 meses)
        meses = []
        faturamentos = []
        despesas = []
        
        meses_para_analisar = 12 if periodo == "anual" else 6
        
        for i in range(meses_para_analisar):
            mes_data = datetime.now().replace(day=1) - timedelta(days=30*i)
            inicio_mes = mes_data.replace(day=1)
            fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Faturamento do mês
            faturamento_mes = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
                LancamentoFinanceiro.tipo == "receita",
                LancamentoFinanceiro.status == "pago",
                LancamentoFinanceiro.data_pagamento.between(inicio_mes, fim_mes)
            ).scalar() or 0
            
            # Despesas do mês
            despesa_mes = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
                LancamentoFinanceiro.tipo == "despesa",
                LancamentoFinanceiro.status == "pago",
                LancamentoFinanceiro.data_pagamento.between(inicio_mes, fim_mes)
            ).scalar() or 0
            
            meses.append(inicio_mes.strftime("%b/%y"))
            faturamentos.append(float(faturamento_mes))
            despesas.append(float(despesa_mes))
        
        meses.reverse()
        faturamentos.reverse()
        despesas.reverse()
        
        # Receita por tipo de serviço (baseado nas categorias de lançamentos)
        categorias_receita = db.query(
            LancamentoFinanceiro.categoria,
            func.sum(LancamentoFinanceiro.valor).label('total')
        ).filter(
            LancamentoFinanceiro.tipo == "receita",
            LancamentoFinanceiro.status == "pago",
            LancamentoFinanceiro.data_pagamento >= date(datetime.now().year, 1, 1)
        ).group_by(LancamentoFinanceiro.categoria).all()
        
        servicos_data = {
            categoria or "Outros": float(total) 
            for categoria, total in categorias_receita
        }
        
        # Distribuição de clientes por regime tributário
        regimes_tributarios = db.query(
            Cliente.regime_tributario,
            func.count(Cliente.id).label('quantidade')
        ).filter(Cliente.ativo == True).group_by(Cliente.regime_tributario).all()
        
        distribuicao_regimes = {
            regime or "Não informado": quantidade
            for regime, quantidade in regimes_tributarios
        }
        
        # Status de obrigações
        status_obrigacoes = db.query(
            ObrigacaoAcessoria.status,
            func.count(ObrigacaoAcessoria.id).label('quantidade')
        ).group_by(ObrigacaoAcessoria.status).all()
        
        status_data = {
            status: quantidade
            for status, quantidade in status_obrigacoes
        }
        
        return {
            "evolucao_faturamento": {
                "labels": meses,
                "faturamento": faturamentos,
                "despesas": despesas
            },
            "receita_servicos": servicos_data,
            "distribuicao_regimes": distribuicao_regimes,
            "status_obrigacoes": status_data
        }
        
    except Exception as e:
        logger.error(f"❌ Erro nos dados dos gráficos: {str(e)}")
        return {
            "evolucao_faturamento": {
                "labels": [],
                "faturamento": [],
                "despesas": []
            },
            "receita_servicos": {},
            "distribuicao_regimes": {},
            "status_obrigacoes": {}
        }

def get_recent_activities(db: Session) -> List[Dict[str, Any]]:
    """Retorna atividades recentes do sistema"""
    
    try:
        atividades = []
        
        # Últimas obrigações entregues (últimos 7 dias)
        data_limite = datetime.now() - timedelta(days=7)
        obrigacoes_entregues = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.status == "entregue",
            ObrigacaoAcessoria.data_entrega >= data_limite.date()
        ).order_by(ObrigacaoAcessoria.data_entrega.desc()).limit(5).all()
        
        for obrigacao in obrigacoes_entregues:
            cliente = db.query(Cliente).filter(Cliente.id == obrigacao.cliente_id).first()
            if cliente:
                atividades.append({
                    "tipo": "obrigacao_entregue",
                    "icone": "check-circle",
                    "titulo": f"{obrigacao.descricao} entregue",
                    "cliente": cliente.nome_razao_social,
                    "data": obrigacao.data_entrega.isoformat() if obrigacao.data_entrega else None,
                    "cor": "success"
                })
        
        # Últimos pagamentos recebidos
        pagamentos = db.query(LancamentoFinanceiro).filter(
            LancamentoFinanceiro.tipo == "receita",
            LancamentoFinanceiro.status == "pago",
            LancamentoFinanceiro.data_pagamento >= data_limite.date()
        ).order_by(LancamentoFinanceiro.data_pagamento.desc()).limit(5).all()
        
        for pagamento in pagamentos:
            cliente = db.query(Cliente).filter(Cliente.id == pagamento.cliente_id).first()
            if cliente:
                atividades.append({
                    "tipo": "pagamento_recebido",
                    "icone": "dollar-sign",
                    "titulo": "Pagamento recebido",
                    "cliente": cliente.nome_razao_social,
                    "data": pagamento.data_pagamento.isoformat() if pagamento.data_pagamento else None,
                    "valor": float(pagamento.valor),
                    "cor": "success"
                })
        
        # Novos clientes (últimos 30 dias)
        data_limite_clientes = datetime.now() - timedelta(days=30)
        novos_clientes = db.query(Cliente).filter(
            Cliente.data_cadastro >= data_limite_clientes
        ).order_by(Cliente.data_cadastro.desc()).limit(3).all()
        
        for cliente in novos_clientes:
            atividades.append({
                "tipo": "novo_cliente",
                "icone": "user-plus",
                "titulo": "Novo cliente cadastrado",
                "cliente": cliente.nome_razao_social,
                "data": cliente.data_cadastro.isoformat() if cliente.data_cadastro else None,
                "cor": "info"
            })
        
        # Novos processos (últimos 15 dias)
        data_limite_processos = datetime.now() - timedelta(days=15)
        novos_processos = db.query(Processo).filter(
            Processo.data_criacao >= data_limite_processos
        ).order_by(Processo.data_criacao.desc()).limit(3).all()
        
        for processo in novos_processos:
            cliente = db.query(Cliente).filter(Cliente.id == processo.cliente_id).first()
            if cliente:
                atividades.append({
                    "tipo": "novo_processo",
                    "icone": "file-text",
                    "titulo": f"Novo processo: {processo.assunto}",
                    "cliente": cliente.nome_razao_social,
                    "data": processo.data_criacao.isoformat() if processo.data_criacao else None,
                    "cor": "warning"
                })
        
        # Ordenar por data e limitar
        atividades_ordenadas = sorted(
            [a for a in atividades if a.get("data")], 
            key=lambda x: x["data"], 
            reverse=True
        )[:8]
        
        return atividades_ordenadas
        
    except Exception as e:
        logger.error(f"❌ Erro nas atividades recentes: {str(e)}")
        return []

def get_top_clients(db: Session, periodo: str = "mensal") -> List[Dict[str, Any]]:
    """Retorna os principais clientes por faturamento"""
    
    try:
        # Definir período
        hoje = datetime.now()
        if periodo == "mensal":
            data_inicio = date(hoje.year, hoje.month, 1)
        elif periodo == "trimestral":
            trimestre_atual = (hoje.month - 1) // 3 + 1
            mes_inicio_trimestre = (trimestre_atual - 1) * 3 + 1
            data_inicio = date(hoje.year, mes_inicio_trimestre, 1)
        else:  # anual
            data_inicio = date(hoje.year, 1, 1)
        
        # Query para clientes com maior faturamento no período
        top_clientes_query = db.query(
            Cliente,
            func.sum(LancamentoFinanceiro.valor).label('faturamento_total')
        ).join(
            LancamentoFinanceiro, 
            LancamentoFinanceiro.cliente_id == Cliente.id
        ).filter(
            LancamentoFinanceiro.tipo == "receita",
            LancamentoFinanceiro.status == "pago",
            LancamentoFinanceiro.data_pagamento >= data_inicio,
            Cliente.ativo == True
        ).group_by(Cliente.id).order_by(
            func.sum(LancamentoFinanceiro.valor).desc()
        ).limit(10).all()
        
        top_clientes = []
        for cliente, faturamento in top_clientes_query:
            # Calcular variação (simplificado - em produção usar período anterior)
            variacao = 8.0  # Em produção, calcular variação real
            
            top_clientes.append({
                "id": cliente.id,
                "nome": cliente.nome_razao_social,
                "faturamento_mensal": float(faturamento or 0),
                "variacao": variacao,
                "regime_tributario": cliente.regime_tributario,
                "data_cadastro": cliente.data_cadastro.isoformat() if cliente.data_cadastro else None
            })
        
        return top_clientes
        
    except Exception as e:
        logger.error(f"❌ Erro nos principais clientes: {str(e)}")
        return []

def get_upcoming_deadlines(db: Session) -> List[Dict[str, Any]]:
    """Retorna os próximos vencimentos"""
    
    try:
        data_limite = date.today() + timedelta(days=30)
        
        # Obrigações acessórias
        obrigacoes = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.data_vencimento <= data_limite,
            ObrigacaoAcessoria.status == "pendente"
        ).order_by(ObrigacaoAcessoria.data_vencimento.asc()).all()
        
        deadlines = []
        for obrigacao in obrigacoes:
            cliente = db.query(Cliente).filter(Cliente.id == obrigacao.cliente_id).first()
            if cliente:
                dias_restantes = (obrigacao.data_vencimento - date.today()).days
                prioridade = "alta" if dias_restantes <= 3 else "media" if dias_restantes <= 7 else "baixa"
                
                deadlines.append({
                    "tipo": "obrigacao",
                    "cliente_nome": cliente.nome_razao_social,
                    "descricao": obrigacao.descricao,
                    "prazo": obrigacao.data_vencimento.isoformat(),
                    "dias_restantes": dias_restantes,
                    "prioridade": prioridade,
                    "tipo_obrigacao": obrigacao.periodicidade
                })
        
        # Prazos processuais
        prazos_processuais = db.query(Processo).filter(
            Processo.data_prazo <= data_limite,
            Processo.data_prazo >= date.today(),
            Processo.status == "ativo"
        ).order_by(Processo.data_prazo.asc()).all()
        
        for processo in prazos_processuais:
            cliente = db.query(Cliente).filter(Cliente.id == processo.cliente_id).first()
            if cliente:
                dias_restantes = (processo.data_prazo - date.today()).days
                prioridade = "alta" if dias_restantes <= 3 else "media" if dias_restantes <= 7 else "baixa"
                
                deadlines.append({
                    "tipo": "processo",
                    "cliente_nome": cliente.nome_razao_social,
                    "descricao": f"Prazo processual: {processo.assunto}",
                    "prazo": processo.data_prazo.isoformat() if processo.data_prazo else None,
                    "dias_restantes": dias_restantes,
                    "prioridade": prioridade,
                    "numero_processo": processo.numero_processo
                })
        
        return sorted(deadlines, key=lambda x: x.get("prazo", ""))[:15]
        
    except Exception as e:
        logger.error(f"❌ Erro nos próximos vencimentos: {str(e)}")
        return []

def get_alerts(db: Session) -> List[Dict[str, Any]]:
    """Retorna alertas e notificações importantes"""
    
    try:
        alerts = []
        
        # Obrigações atrasadas
        obrigacoes_atrasadas = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.status == "pendente",
            ObrigacaoAcessoria.data_vencimento < date.today()
        ).count()
        
        if obrigacoes_atrasadas > 0:
            alerts.append({
                "tipo": "warning",
                "titulo": "Obrigações Atrasadas",
                "mensagem": f"{obrigacoes_atrasadas} obrigações estão com prazo vencido",
                "icone": "alert-triangle"
            })
        
        # Lançamentos em atraso
        lancamentos_atrasados = db.query(LancamentoFinanceiro).filter(
            LancamentoFinanceiro.status == "atrasado",
            LancamentoFinanceiro.tipo == "receita"
        ).count()
        
        if lancamentos_atrasados > 0:
            alerts.append({
                "tipo": "danger",
                "titulo": "Inadimplência",
                "mensagem": f"{lancamentos_atrasados} pagamentos em atraso",
                "icone": "trending-down"
            })
        
        # Clientes sem atividade recente (últimos 90 dias)
        data_limite = datetime.now() - timedelta(days=90)
        clientes_inativos = db.query(Cliente).filter(
            Cliente.ativo == True,
            Cliente.updated_at < data_limite
        ).count()
        
        if clientes_inativos > 0:
            alerts.append({
                "tipo": "info",
                "titulo": "Clientes Inativos",
                "mensagem": f"{clientes_inativos} clientes sem atividade recente",
                "icone": "users"
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"❌ Erro nos alertas: {str(e)}")
        return []

def get_performance_by_area(db: Session, periodo: str = "mensal") -> Dict[str, Any]:
    """Retorna performance por área (contábil, jurídica, fiscal)"""
    
    try:
        # Definir período
        hoje = datetime.now()
        if periodo == "mensal":
            data_inicio = date(hoje.year, hoje.month, 1)
        elif periodo == "trimestral":
            trimestre_atual = (hoje.month - 1) // 3 + 1
            mes_inicio_trimestre = (trimestre_atual - 1) * 3 + 1
            data_inicio = date(hoje.year, mes_inicio_trimestre, 1)
        else:  # anual
            data_inicio = date(hoje.year, 1, 1)
        
        # Performance Contábil
        # 🔥 CORREÇÃO: DRE usa periodo (String) em vez de mes_referencia
        dre_mes = db.query(DRE).filter(DRE.periodo >= data_inicio.strftime("%Y-%m")).count()
        obrigacoes_entregues = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.status == "entregue",
            ObrigacaoAcessoria.data_entrega >= data_inicio
        ).count()
        
        # Performance Jurídica
        processos_ativos = db.query(Processo).filter(
            Processo.status == "ativo"
        ).count()
        andamentos_recentes = db.query(AndamentoProcessual).filter(
            AndamentoProcessual.data_andamento >= data_inicio
        ).count()
        
        # Performance Fiscal
        notas_emitidas = db.query(NotaFiscal).filter(
            NotaFiscal.data_emissao >= data_inicio,
            NotaFiscal.situacao == "autorizada"
        ).count()
        
        return {
            "contabil": {
                "dres_gerados": dre_mes,
                "obrigacoes_entregues": obrigacoes_entregues,
                "performance": min(100, (dre_mes + obrigacoes_entregues) * 10)
            },
            "juridico": {
                "processos_ativos": processos_ativos,
                "andamentos_recentes": andamentos_recentes,
                "performance": min(100, processos_ativos * 5 + andamentos_recentes * 2)
            },
            "fiscal": {
                "notas_emitidas": notas_emitidas,
                "performance": min(100, notas_emitidas * 10)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na performance por área: {str(e)}")
        return {
            "contabil": {"dres_gerados": 0, "obrigacoes_entregues": 0, "performance": 0},
            "juridico": {"processos_ativos": 0, "andamentos_recentes": 0, "performance": 0},
            "fiscal": {"notas_emitidas": 0, "performance": 0}
        }

# Endpoint específico para métricas rápidas
@router.get("/metrics/quick")
def get_quick_metrics(db: Session = Depends(get_db)):
    """Retorna apenas as métricas principais para carregamento rápido"""
    return get_main_metrics(db)

# Endpoint para dados de um cliente específico no dashboard
@router.get("/cliente/{cliente_id}")
def get_cliente_dashboard(cliente_id: str, db: Session = Depends(get_db)):
    """Retorna dados do dashboard para um cliente específico"""
    
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Métricas do cliente
        faturamento_cliente = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.cliente_id == cliente_id,
            LancamentoFinanceiro.tipo == "receita",
            LancamentoFinanceiro.status == "pago"
        ).scalar() or 0
        
        obrigacoes_pendentes = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.cliente_id == cliente_id,
            ObrigacaoAcessoria.status == "pendente"
        ).count()
        
        processos_ativos = db.query(Processo).filter(
            Processo.cliente_id == cliente_id,
            Processo.status == "ativo"
        ).count()
        
        # 🔥 CORREÇÃO: Verificar se contratos existe antes de acessar
        total_contratos = 0
        if hasattr(cliente, 'contratos'):
            total_contratos = len(cliente.contratos)
        
        return {
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome_razao_social,
                "cnpj_cpf": cliente.cnpj_cpf,
                "regime_tributario": cliente.regime_tributario
            },
            "metrics": {
                "faturamento_total": float(faturamento_cliente),
                "obrigacoes_pendentes": obrigacoes_pendentes,
                "processos_ativos": processos_ativos,
                "total_contratos": total_contratos
            },
            "atividades_recentes": get_recent_activities_for_cliente(db, cliente_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no dashboard do cliente: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao carregar dados do cliente")

def get_recent_activities_for_cliente(db: Session, cliente_id: str) -> List[Dict[str, Any]]:
    """Retorna atividades recentes para um cliente específico"""
    
    try:
        atividades = []
        
        # Últimas obrigações
        obrigacoes = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.cliente_id == cliente_id
        ).order_by(ObrigacaoAcessoria.updated_at.desc()).limit(5).all()
        
        for obrigacao in obrigacoes:
            atividades.append({
                "tipo": "obrigacao",
                "descricao": obrigacao.descricao,
                "status": obrigacao.status,
                "data": obrigacao.updated_at.isoformat() if obrigacao.updated_at else None
            })
        
        # Últimos lançamentos
        lancamentos = db.query(LancamentoFinanceiro).filter(
            LancamentoFinanceiro.cliente_id == cliente_id
        ).order_by(LancamentoFinanceiro.updated_at.desc()).limit(5).all()
        
        for lancamento in lancamentos:
            atividades.append({
                "tipo": "lancamento",
                "descricao": lancamento.descricao,
                "valor": float(lancamento.valor),
                "status": lancamento.status,
                "data": lancamento.updated_at.isoformat() if lancamento.updated_at else None
            })
        
        return sorted(atividades, key=lambda x: x.get("data", ""), reverse=True)[:10]
        
    except Exception as e:
        logger.error(f"❌ Erro nas atividades do cliente: {str(e)}")
        return []