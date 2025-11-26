from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta
import logging

from ..models.database import get_db
from ..models.financeiro import LancamentoFinanceiro, IndicadorFinanceiro
from ..models.clientes import Cliente
from ..schemas.financeiro import (
    LancamentoFinanceiro as LancamentoSchema,
    LancamentoFinanceiroCreate,
    LancamentoFinanceiroUpdate,
    IndicadorFinanceiro as IndicadorSchema,
    IndicadorFinanceiroCreate,
    FluxoCaixaResponse,
    DashboardFinanceiroResponse
)

router = APIRouter(prefix="/financeiro", tags=["financeiro"])
logger = logging.getLogger(__name__)

# 📊 LANÇAMENTOS FINANCEIROS

@router.get("/lancamentos/", response_model=List[LancamentoSchema])
def listar_lancamentos(
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[str] = None,
    tipo: Optional[str] = Query(None, regex="^(receita|despesa)$"),
    status: Optional[str] = Query(None, regex="^(pendente|pago|atrasado|cancelado)$"),  # ✅ CORREÇÃO: adicionado cancelado
    categoria: Optional[str] = None,
    data_vencimento_inicio: Optional[date] = None,
    data_vencimento_fim: Optional[date] = None,
    data_pagamento_inicio: Optional[date] = None,
    data_pagamento_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Lista lançamentos financeiros com filtros avançados
    """
    try:
        query = db.query(LancamentoFinanceiro)
        
        # Aplicar filtros
        if cliente_id:
            query = query.filter(LancamentoFinanceiro.cliente_id == cliente_id)
        
        if tipo:
            query = query.filter(LancamentoFinanceiro.tipo == tipo)
        
        if status:
            query = query.filter(LancamentoFinanceiro.status == status)
        
        if categoria:
            query = query.filter(LancamentoFinanceiro.categoria == categoria)
        
        if data_vencimento_inicio:
            query = query.filter(LancamentoFinanceiro.data_vencimento >= data_vencimento_inicio)
        
        if data_vencimento_fim:
            query = query.filter(LancamentoFinanceiro.data_vencimento <= data_vencimento_fim)
        
        if data_pagamento_inicio:
            query = query.filter(LancamentoFinanceiro.data_pagamento >= data_pagamento_inicio)
        
        if data_pagamento_fim:
            query = query.filter(LancamentoFinanceiro.data_pagamento <= data_pagamento_fim)
        
        lancamentos = query.order_by(LancamentoFinanceiro.data_vencimento.desc()).offset(skip).limit(limit).all()
        return lancamentos
        
    except Exception as e:
        logger.error(f"Erro ao listar lançamentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar lançamentos"
        )

@router.get("/lancamentos/{lancamento_id}", response_model=LancamentoSchema)
def obter_lancamento(lancamento_id: str, db: Session = Depends(get_db)):
    """
    Obtém um lançamento financeiro específico pelo ID
    """
    try:
        lancamento = db.query(LancamentoFinanceiro).filter(LancamentoFinanceiro.id == lancamento_id).first()
        if not lancamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        return lancamento
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter lançamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter lançamento"
        )

@router.post("/lancamentos/", response_model=LancamentoSchema, status_code=status.HTTP_201_CREATED)
def criar_lancamento(lancamento: LancamentoFinanceiroCreate, db: Session = Depends(get_db)):
    """
    Cria um novo lançamento financeiro
    """
    try:
        # Verificar se o cliente existe
        if lancamento.cliente_id:
            cliente = db.query(Cliente).filter(Cliente.id == lancamento.cliente_id).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
        
        db_lancamento = LancamentoFinanceiro(**lancamento.model_dump())
        
        db.add(db_lancamento)
        db.commit()
        db.refresh(db_lancamento)
        return db_lancamento
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar lançamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar lançamento"
        )

@router.patch("/lancamentos/{lancamento_id}", response_model=LancamentoSchema)
def atualizar_lancamento_parcial(
    lancamento_id: str,
    lancamento_update: LancamentoFinanceiroUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente um lançamento financeiro
    """
    try:
        db_lancamento = db.query(LancamentoFinanceiro).filter(LancamentoFinanceiro.id == lancamento_id).first()
        if not db_lancamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        
        update_data = lancamento_update.model_dump(exclude_unset=True)
        
        # Verificar se cliente existe se estiver sendo atualizado
        if 'cliente_id' in update_data and update_data['cliente_id']:
            cliente = db.query(Cliente).filter(Cliente.id == update_data['cliente_id']).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
        
        for key, value in update_data.items():
            setattr(db_lancamento, key, value)
        
        db.commit()
        db.refresh(db_lancamento)
        return db_lancamento
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar lançamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar lançamento"
        )

@router.post("/lancamentos/{lancamento_id}/pagar", response_model=LancamentoSchema)
def marcar_como_pago(
    lancamento_id: str,
    data_pagamento: Optional[date] = None,
    forma_pagamento: Optional[str] = None,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Marca um lançamento como pago/recebido
    """
    try:
        lancamento = db.query(LancamentoFinanceiro).filter(LancamentoFinanceiro.id == lancamento_id).first()
        if not lancamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        
        lancamento.status = "pago"
        lancamento.data_pagamento = data_pagamento or date.today()
        
        if forma_pagamento:
            lancamento.forma_pagamento = forma_pagamento
        
        if observacoes:
            lancamento.observacoes = observacoes
        
        db.commit()
        db.refresh(lancamento)
        return lancamento
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao marcar como pago: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao marcar como pago"
        )

@router.delete("/lancamentos/{lancamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_lancamento(lancamento_id: str, db: Session = Depends(get_db)):
    """
    Exclui um lançamento financeiro
    """
    try:
        lancamento = db.query(LancamentoFinanceiro).filter(LancamentoFinanceiro.id == lancamento_id).first()
        if not lancamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        
        db.delete(lancamento)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao excluir lançamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir lançamento"
        )

# 📈 INDICADORES FINANCEIROS

@router.get("/indicadores/", response_model=List[IndicadorSchema])
def listar_indicadores(
    cliente_id: Optional[str] = None,
    mes_referencia: Optional[date] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Lista indicadores financeiros com filtros
    """
    try:
        query = db.query(IndicadorFinanceiro)
        
        if cliente_id:
            query = query.filter(IndicadorFinanceiro.cliente_id == cliente_id)
        
        if mes_referencia:
            query = query.filter(IndicadorFinanceiro.mes_referencia == mes_referencia)
        
        if ano:
            query = query.filter(IndicadorFinanceiro.mes_referencia >= date(ano, 1, 1))
            query = query.filter(IndicadorFinanceiro.mes_referencia <= date(ano, 12, 31))
        
        indicadores = query.order_by(IndicadorFinanceiro.mes_referencia.desc()).all()
        return indicadores
        
    except Exception as e:
        logger.error(f"Erro ao listar indicadores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar indicadores"
        )

@router.post("/indicadores/", response_model=IndicadorSchema, status_code=status.HTTP_201_CREATED)
def criar_indicador(indicador: IndicadorFinanceiroCreate, db: Session = Depends(get_db)):
    """
    Cria um novo indicador financeiro
    """
    try:
        # Verificar se já existe indicador para o mesmo cliente e mês
        indicador_existente = db.query(IndicadorFinanceiro).filter(
            IndicadorFinanceiro.cliente_id == indicador.cliente_id,
            IndicadorFinanceiro.mes_referencia == indicador.mes_referencia
        ).first()
        
        if indicador_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um indicador para este cliente no mês de referência"
            )
        
        db_indicador = IndicadorFinanceiro(**indicador.model_dump())
        
        db.add(db_indicador)
        db.commit()
        db.refresh(db_indicador)
        return db_indicador
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar indicador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar indicador"
        )

# 🔄 RELATÓRIOS E ESTATÍSTICAS

@router.get("/fluxo-caixa/", response_model=FluxoCaixaResponse)
def obter_fluxo_caixa(
    data_inicio: date,
    data_fim: date,
    cliente_id: Optional[str] = None,  # 🔥 CORREÇÃO: str em vez de UUID
    agrupar_por: str = Query("dia", regex="^(dia|semana|mes)$"),
    db: Session = Depends(get_db)
):
    """
    Retorna o fluxo de caixa detalhado no período
    """
    query = db.query(LancamentoFinanceiro).filter(
        LancamentoFinanceiro.data_vencimento.between(data_inicio, data_fim)
    )
    
    if cliente_id:
        query = query.filter(LancamentoFinanceiro.cliente_id == cliente_id)  # 🔥 CORREÇÃO: sem str()
    
    lancamentos = query.all()
    
    # Totais gerais
    receitas = sum(l.valor for l in lancamentos if l.tipo == "receita")
    despesas = sum(l.valor for l in lancamentos if l.tipo == "despesa")
    saldo = receitas - despesas
    
    # Agrupar por período
    fluxo_detalhado = {}
    for lancamento in lancamentos:
        if agrupar_por == "dia":
            chave = lancamento.data_vencimento.isoformat()
        elif agrupar_por == "semana":
            # Segunda-feira como início da semana
            inicio_semana = lancamento.data_vencimento - timedelta(days=lancamento.data_vencimento.weekday())
            chave = inicio_semana.isoformat()
        else:  # mês
            chave = lancamento.data_vencimento.strftime("%Y-%m-01")
        
        if chave not in fluxo_detalhado:
            fluxo_detalhado[chave] = {"receitas": 0, "despesas": 0, "saldo": 0}
        
        if lancamento.tipo == "receita":
            fluxo_detalhado[chave]["receitas"] += lancamento.valor
        else:
            fluxo_detalhado[chave]["despesas"] += lancamento.valor
        
        fluxo_detalhado[chave]["saldo"] = fluxo_detalhado[chave]["receitas"] - fluxo_detalhado[chave]["despesas"]
    
    # Estatísticas adicionais
    receitas_pagas = sum(l.valor for l in lancamentos if l.tipo == "receita" and l.status == "pago")
    despesas_pagas = sum(l.valor for l in lancamentos if l.tipo == "despesa" and l.status == "pago")
    receitas_pendentes = sum(l.valor for l in lancamentos if l.tipo == "receita" and l.status in ["pendente", "atrasado"])
    despesas_pendentes = sum(l.valor for l in lancamentos if l.tipo == "despesa" and l.status in ["pendente", "atrasado"])
    
    return {
        "periodo": {
            "inicio": data_inicio,
            "fim": data_fim
        },
        "totais": {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": saldo
        },
        "realizado": {
            "receitas": receitas_pagas,
            "despesas": despesas_pagas,
            "saldo": receitas_pagas - despesas_pagas
        },
        "pendente": {
            "receitas": receitas_pendentes,
            "despesas": despesas_pendentes
        },
        "fluxo_detalhado": fluxo_detalhado,
        "total_lancamentos": len(lancamentos)
    }

@router.get("/dashboard/")
def dashboard_financeiro(
    periodo: str = Query("mensal", regex="^(mensal|trimestral|anual)$"),
    db: Session = Depends(get_db)
):
    """
    Dashboard com métricas financeiras consolidadas
    """
    hoje = datetime.now()
    
    if periodo == "mensal":
        data_inicio = date(hoje.year, hoje.month, 1)
    elif periodo == "trimestral":
        trimestre_atual = (hoje.month - 1) // 3 + 1
        mes_inicio = (trimestre_atual - 1) * 3 + 1
        data_inicio = date(hoje.year, mes_inicio, 1)
    else:  # anual
        data_inicio = date(hoje.year, 1, 1)
    
    # Métricas principais
    total_receitas = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
        LancamentoFinanceiro.tipo == "receita",
        LancamentoFinanceiro.status == "pago",
        LancamentoFinanceiro.data_pagamento >= data_inicio
    ).scalar() or 0
    
    total_despesas = db.query(func.sum(LancamentoFinanceiro.valor)).filter(
        LancamentoFinanceiro.tipo == "despesa",
        LancamentoFinanceiro.status == "pago",
        LancamentoFinanceiro.data_pagamento >= data_inicio
    ).scalar() or 0
    
    # Receitas por categoria
    receitas_por_categoria = db.query(
        LancamentoFinanceiro.categoria,
        func.sum(LancamentoFinanceiro.valor).label('total')
    ).filter(
        LancamentoFinanceiro.tipo == "receita",
        LancamentoFinanceiro.status == "pago",
        LancamentoFinanceiro.data_pagamento >= data_inicio
    ).group_by(LancamentoFinanceiro.categoria).all()
    
    # Despesas por categoria
    despesas_por_categoria = db.query(
        LancamentoFinanceiro.categoria,
        func.sum(LancamentoFinanceiro.valor).label('total')
    ).filter(
        LancamentoFinanceiro.tipo == "despesa",
        LancamentoFinanceiro.status == "pago",
        LancamentoFinanceiro.data_pagamento >= data_inicio
    ).group_by(LancamentoFinanceiro.categoria).all()
    
    # Top clientes (por faturamento)
    top_clientes = db.query(
        Cliente.nome_razao_social,
        func.sum(LancamentoFinanceiro.valor).label('faturamento')
    ).join(
        LancamentoFinanceiro, LancamentoFinanceiro.cliente_id == Cliente.id
    ).filter(
        LancamentoFinanceiro.tipo == "receita",
        LancamentoFinanceiro.status == "pago",
        LancamentoFinanceiro.data_pagamento >= data_inicio
    ).group_by(Cliente.id, Cliente.nome_razao_social).order_by(
        func.sum(LancamentoFinanceiro.valor).desc()
    ).limit(5).all()
    
    return {
        "periodo": periodo,
        "data_inicio": data_inicio,
        "metricas_principais": {
            "receitas": float(total_receitas),
            "despesas": float(total_despesas),
            "lucro_liquido": float(total_receitas - total_despesas),
            "margem_lucro": ((total_receitas - total_despesas) / total_receitas * 100) if total_receitas > 0 else 0
        },
        "receitas_por_categoria": {
            categoria: float(total) for categoria, total in receitas_por_categoria
        },
        "despesas_por_categoria": {
            categoria: float(total) for categoria, total in despesas_por_categoria
        },
        "top_clientes": [
            {"nome": nome, "faturamento": float(faturamento)} for nome, faturamento in top_clientes
        ]
    }

@router.get("/previsao-caixa/")
def previsao_caixa(
    dias: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Previsão de fluxo de caixa para os próximos dias
    """
    hoje = date.today()
    data_fim = hoje + timedelta(days=dias)
    
    # Lançamentos futuros
    lancamentos_futuros = db.query(LancamentoFinanceiro).filter(
        LancamentoFinanceiro.data_vencimento.between(hoje, data_fim),
        LancamentoFinanceiro.status.in_(["pendente", "atrasado"])
    ).all()
    
    previsao = {}
    saldo_acumulado = 0
    
    for i in range(dias + 1):
        data = hoje + timedelta(days=i)
        chave = data.isoformat()
        
        receitas_dia = sum(l.valor for l in lancamentos_futuros if l.tipo == "receita" and l.data_vencimento == data)
        despesas_dia = sum(l.valor for l in lancamentos_futuros if l.tipo == "despesa" and l.data_vencimento == data)
        saldo_dia = receitas_dia - despesas_dia
        saldo_acumulado += saldo_dia
        
        previsao[chave] = {
            "receitas": receitas_dia,
            "despesas": despesas_dia,
            "saldo_dia": saldo_dia,
            "saldo_acumulado": saldo_acumulado
        }
    
    return {
        "periodo": {
            "inicio": hoje,
            "fim": data_fim,
            "dias": dias
        },
        "previsao": previsao,
        "total_receitas_previstas": sum(v["receitas"] for v in previsao.values()),
        "total_despesas_previstas": sum(v["despesas"] for v in previsao.values()),
        "saldo_final_previsto": saldo_acumulado
    }