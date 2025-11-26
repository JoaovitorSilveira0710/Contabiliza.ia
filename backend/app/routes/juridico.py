from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from ..models.database import get_db
from ..models.juridico import Processo, AndamentoProcessual, Audiencia
from ..models.clientes import Cliente
from ..schemas.juridico import (
    Processo as ProcessoSchema,
    ProcessoCreate,
    ProcessoUpdate,
    AndamentoProcessual as AndamentoSchema,
    AndamentoProcessualCreate,
    AndamentoProcessualUpdate,
    Audiencia as AudienciaSchema,
    AudienciaCreate,
    DashboardJuridicoResponse
)

router = APIRouter(prefix="/juridico", tags=["juridico"])
logger = logging.getLogger(__name__)

# ⚖️ TESTE SIMPLES
@router.get("/test")
def test_endpoint():
    """Endpoint de teste simples"""
    return {"status": "ok", "message": "Juridico funcionando"}

# ⚖️ PROCESSOS JUDICIAIS

@router.get("/processos/")
def listar_processos(
    db: Session = Depends(get_db)
):
    """
    Lista processos judiciais
    """
    try:
        processos = db.query(Processo).limit(100).all()
        
        # Converter para dicionários simples
        result = []
        for p in processos:
            result.append({
                "id": p.id,
                "numero_processo": p.numero_processo,
                "assunto": p.assunto,
                "status": p.status,
                "cliente_id": p.cliente_id,
                "vara": p.vara,
                "data_distribuicao": p.data_distribuicao.isoformat() if p.data_distribuicao else None,
                "tipo_acao": p.tipo_acao,
                "valor_causa": p.valor_causa,
                "honorarios": p.honorarios,
                "honorarios_contratuais": p.honorarios_contratuais,
                "parte_contraria": p.parte_contraria,
                "advogado_responsavel": p.advogado_responsavel,
                "data_prazo": p.data_prazo.isoformat() if p.data_prazo else None,
                "ultima_movimentacao": p.ultima_movimentacao,
                "data_ultima_movimentacao": p.data_ultima_movimentacao.isoformat() if p.data_ultima_movimentacao else None,
                "observacoes": p.observacoes,
                "data_criacao": p.data_criacao.isoformat() if p.data_criacao else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao listar processos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )

@router.get("/processos/{processo_id}", response_model=ProcessoSchema)
def obter_processo(processo_id: str, db: Session = Depends(get_db)):
    """
    Obtém um processo específico pelo ID
    """
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        if not processo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processo não encontrado"
            )
        return processo
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter processo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter processo"
        )

@router.post("/processos/", response_model=ProcessoSchema, status_code=status.HTTP_201_CREATED)
def criar_processo(processo: ProcessoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo processo judicial
    """
    try:
        # Verificar se número do processo já existe
        processo_existente = db.query(Processo).filter(
            Processo.numero_processo == processo.numero_processo
        ).first()
        
        if processo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número do processo já cadastrado"
            )
        
        # Verificar se cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == processo.cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente não encontrado"
            )
        
        db_processo = Processo(**processo.model_dump())
        db.add(db_processo)
        db.commit()
        db.refresh(db_processo)
        return db_processo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar processo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar processo"
        )

@router.patch("/processos/{processo_id}", response_model=ProcessoSchema)
def atualizar_processo_parcial(
    processo_id: str,
    processo_update: ProcessoUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente um processo judicial
    """
    try:
        db_processo = db.query(Processo).filter(Processo.id == processo_id).first()
        if not db_processo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processo não encontrado"
            )
        
        update_data = processo_update.model_dump(exclude_unset=True)
        
        # Verificar unicidade se estiver atualizando número do processo
        if 'numero_processo' in update_data:
            processo_existente = db.query(Processo).filter(
                Processo.numero_processo == update_data['numero_processo'],
                Processo.id != processo_id
            ).first()
            
            if processo_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Número do processo já cadastrado em outro processo"
                )
        
        # Verificar cliente se estiver sendo atualizado
        if 'cliente_id' in update_data:
            cliente = db.query(Cliente).filter(Cliente.id == update_data['cliente_id']).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
        
        for key, value in update_data.items():
            setattr(db_processo, key, value)
        
        db.commit()
        db.refresh(db_processo)
        return db_processo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar processo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar processo"
        )

@router.post("/processos/{processo_id}/encerrar", response_model=ProcessoSchema)
def encerrar_processo(
    processo_id: str,
    resultado: Optional[str] = None,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Encerra um processo judicial
    """
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        if not processo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processo não encontrado"
            )
        
        processo.status = "encerrado"
        processo.data_conclusao = date.today()
        
        if observacoes:
            if processo.observacoes:
                processo.observacoes += f"\nEncerramento: {observacoes}"
            else:
                processo.observacoes = f"Encerramento: {observacoes}"
        
        # Criar andamento automático
        andamento = AndamentoProcessual(
            processo_id=processo_id,
            descricao=f"Processo encerrado. Resultado: {resultado or 'Não informado'}",
            tipo="sentenca",
            resultado="favoravel" if resultado and "favor" in resultado.lower() else "desfavoravel"
        )
        db.add(andamento)
        
        db.commit()
        db.refresh(processo)
        return processo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao encerrar processo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao encerrar processo"
        )

@router.delete("/processos/{processo_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_processo(processo_id: str, db: Session = Depends(get_db)):
    """
    Exclui um processo judicial
    """
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        if not processo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processo não encontrado"
            )
        
        db.delete(processo)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao excluir processo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir processo"
        )

# 📅 ANDAMENTOS PROCESSUAIS

@router.get("/processos/{processo_id}/andamentos", response_model=List[AndamentoSchema])
def listar_andamentos_processo(
    processo_id: str,
    tipo: Optional[str] = None,
    resultado: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Lista andamentos de um processo com filtros
    """
    try:
        query = db.query(AndamentoProcessual).filter(
            AndamentoProcessual.processo_id == processo_id
        )
        
        if tipo:
            query = query.filter(AndamentoProcessual.tipo == tipo)
        
        if resultado:
            query = query.filter(AndamentoProcessual.resultado == resultado)
        
        if data_inicio:
            query = query.filter(AndamentoProcessual.data_andamento >= data_inicio)
        
        if data_fim:
            query = query.filter(AndamentoProcessual.data_andamento <= data_fim)
        
        andamentos = query.order_by(AndamentoProcessual.data_andamento.desc()).all()
        return andamentos
        
    except Exception as e:
        logger.error(f"Erro ao listar andamentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar andamentos"
        )

@router.post("/andamentos/", response_model=AndamentoSchema, status_code=status.HTTP_201_CREATED)
def criar_andamento(andamento: AndamentoProcessualCreate, db: Session = Depends(get_db)):
    """
    Cria um novo andamento processual
    """
    try:
        # Verificar se processo existe
        processo = db.query(Processo).filter(Processo.id == andamento.processo_id).first()
        if not processo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processo não encontrado"
            )
        
        db_andamento = AndamentoProcessual(**andamento.model_dump())
        db.add(db_andamento)
        
        # Atualizar última movimentação do processo
        processo.ultima_movimentacao = andamento.descricao
        processo.data_ultima_movimentacao = andamento.data_andamento.date()
        
        # Se for uma sentença, verificar se encerra o processo
        if andamento.tipo == "sentenca" and andamento.resultado in ["favoravel", "desfavoravel"]:
            processo.status = "encerrado"
            processo.data_conclusao = andamento.data_andamento.date()
        
        db.commit()
        db.refresh(db_andamento)
        return db_andamento
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar andamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar andamento"
        )

@router.patch("/andamentos/{andamento_id}", response_model=AndamentoSchema)
def atualizar_andamento_parcial(
    andamento_id: str,
    andamento_update: AndamentoProcessualUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente um andamento processual
    """
    try:
        db_andamento = db.query(AndamentoProcessual).filter(AndamentoProcessual.id == andamento_id).first()
        if not db_andamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Andamento não encontrado"
            )
        
        update_data = andamento_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_andamento, key, value)
        
        db.commit()
        db.refresh(db_andamento)
        return db_andamento
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar andamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar andamento"
        )

@router.delete("/andamentos/{andamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_andamento(andamento_id: str, db: Session = Depends(get_db)):
    """
    Exclui um andamento processual
    """
    try:
        andamento = db.query(AndamentoProcessual).filter(AndamentoProcessual.id == andamento_id).first()
        if not andamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Andamento não encontrado"
            )
        
        db.delete(andamento)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao excluir andamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir andamento"
        )

# 🎯 AUDIÊNCIAS

@router.get("/audiencias/", response_model=List[AudienciaSchema])
def listar_audiencias(
    processo_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista audiências com filtros
    """
    try:
        query = db.query(Audiencia)
        
        if processo_id:
            query = query.filter(Audiencia.processo_id == processo_id)
        
        if data_inicio:
            query = query.filter(Audiencia.data_audiencia >= data_inicio)
        
        if data_fim:
            query = query.filter(Audiencia.data_audiencia <= data_fim)
        
        if tipo:
            query = query.filter(Audiencia.tipo == tipo)
        
        audiencias = query.order_by(Audiencia.data_audiencia.asc()).all()
        return audiencias
        
    except Exception as e:
        logger.error(f"Erro ao listar audiências: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar audiências"
        )

@router.post("/audiencias/", response_model=AudienciaSchema, status_code=status.HTTP_201_CREATED)
def criar_audiencia(audiencia: AudienciaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova audiência
    """
    try:
        # Verificar se processo existe
        processo = db.query(Processo).filter(Processo.id == audiencia.processo_id).first()
        if not processo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processo não encontrado"
            )
        
        db_audiencia = Audiencia(**audiencia.model_dump())
        db.add(db_audiencia)
        db.commit()
        db.refresh(db_audiencia)
        return db_audiencia
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar audiência: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar audiência"
        )

@router.post("/audiencias/{audiencia_id}/realizar", response_model=AudienciaSchema)
def realizar_audiencia(
    audiencia_id: str,
    resultado: str,
    comparecimento: bool = True,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Marca uma audiência como realizada
    """
    try:
        audiencia = db.query(Audiencia).filter(Audiencia.id == audiencia_id).first()
        if not audiencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audiência não encontrada"
            )
        
        audiencia.resultado = resultado
        audiencia.comparecimento = comparecimento
        audiencia.observacoes = observacoes
        
        # Criar andamento automático
        andamento = AndamentoProcessual(
            processo_id=audiencia.processo_id,
            descricao=f"Audiência realizada: {resultado}. Comparecimento: {'Sim' if comparecimento else 'Não'}",
            tipo="audiencia",
            resultado="favoravel" if "favor" in resultado.lower() else "desfavoravel"
        )
        db.add(andamento)
        
        db.commit()
        db.refresh(audiencia)
        return audiencia
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao realizar audiência: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao realizar audiência"
        )

@router.patch("/audiencias/{audiencia_id}", response_model=AudienciaSchema)
def atualizar_audiencia_parcial(
    audiencia_id: str,
    audiencia_update: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente uma audiência
    """
    try:
        db_audiencia = db.query(Audiencia).filter(Audiencia.id == audiencia_id).first()
        if not db_audiencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audiência não encontrada"
            )
        
        for key, value in audiencia_update.items():
            if hasattr(db_audiencia, key):
                setattr(db_audiencia, key, value)
        
        db.commit()
        db.refresh(db_audiencia)
        return db_audiencia
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar audiência: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar audiência"
        )

@router.delete("/audiencias/{audiencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_audiencia(audiencia_id: str, db: Session = Depends(get_db)):
    """
    Exclui uma audiência
    """
    try:
        audiencia = db.query(Audiencia).filter(Audiencia.id == audiencia_id).first()
        if not audiencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audiência não encontrada"
            )
        
        db.delete(audiencia)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao excluir audiência: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir audiência"
        )

# 📊 RELATÓRIOS E ESTATÍSTICAS

@router.get("/relatorios/processos-ativos", response_model=Dict[str, Any])
def relatorio_processos_ativos(db: Session = Depends(get_db)):
    """
    Relatório detalhado de processos ativos
    """
    try:
        processos_ativos = db.query(Processo).filter(Processo.status == "ativo").all()
        
        total_honorarios = sum(p.honorarios or 0 for p in processos_ativos)
        total_honorarios_contratuais = sum(p.honorarios_contratuais or 0 for p in processos_ativos)
        total_valor_causa = sum(p.valor_causa or 0 for p in processos_ativos)
        
        # Processos por tipo de ação
        processos_por_tipo = db.query(
            Processo.tipo_acao,
            func.count(Processo.id).label('quantidade')
        ).filter(Processo.status == "ativo").group_by(Processo.tipo_acao).all()
        
        # Processos com prazos próximos
        data_limite = date.today() + timedelta(days=7)
        processos_prazo_proximo = db.query(Processo).filter(
            Processo.status == "ativo",
            Processo.data_prazo <= data_limite,
            Processo.data_prazo >= date.today()
        ).count()
        
        processos_prazo_vencido = db.query(Processo).filter(
            Processo.status == "ativo",
            Processo.data_prazo < date.today()
        ).count()
        
        return {
            "total_processos_ativos": len(processos_ativos),
            "total_honorarios_estimados": total_honorarios,
            "total_honorarios_contratuais": total_honorarios_contratuais,
            "total_valor_causa": total_valor_causa,
            "processos_por_cliente": len(set(p.cliente_id for p in processos_ativos)),
            "processos_por_tipo": dict(processos_por_tipo),
            "processos_prazo_proximo": processos_prazo_proximo,
            "processos_prazo_vencido": processos_prazo_vencido,
            "honorarios_devidos": max(0, total_honorarios_contratuais - total_honorarios)
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de processos ativos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório"
        )

@router.get("/relatorios/processos-sem-movimentacao")
def processos_sem_movimentacao(
    dias: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Processos sem movimentação há X dias
    """
    try:
        data_limite = datetime.now().date() - timedelta(days=dias)
        
        processos_sem_mov = db.query(Processo).filter(
            Processo.status == "ativo",
            or_(
                Processo.data_ultima_movimentacao.is_(None),
                Processo.data_ultima_movimentacao < data_limite
            )
        ).all()
        
        return {
            "dias_sem_movimentacao": dias,
            "total_processos": len(processos_sem_mov),
            "processos": [
                {
                    "id": p.id,
                    "numero_processo": p.numero_processo,
                    "cliente": p.cliente.nome_razao_social if p.cliente else "N/A",
                    "ultima_movimentacao": p.data_ultima_movimentacao,
                    "dias_sem_movimentacao": (date.today() - p.data_ultima_movimentacao).days if p.data_ultima_movimentacao else None
                }
                for p in processos_sem_mov
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de processos sem movimentação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório"
        )

@router.get("/relatorios/performance-advogados")
def performance_advogados(
    data_inicio: date,
    data_fim: date,
    db: Session = Depends(get_db)
):
    """
    Performance dos advogados por período
    """
    try:
        # Andamentos por advogado
        andamentos_por_advogado = db.query(
            AndamentoProcessual.usuario_responsavel,
            func.count(AndamentoProcessual.id).label('total_andamentos'),
            func.avg(
                case(
                    [(AndamentoProcessual.resultado == 'favoravel', 1)],
                    else_=0
                )
            ).label('taxa_sucesso')
        ).filter(
            AndamentoProcessual.data_andamento.between(data_inicio, data_fim),
            AndamentoProcessual.usuario_responsavel.isnot(None)
        ).group_by(AndamentoProcessual.usuario_responsavel).all()
        
        return {
            "periodo": {"inicio": data_inicio, "fim": data_fim},
            "performance_advogados": [
                {
                    "advogado": advogado,
                    "total_andamentos": total_andamentos,
                    "taxa_sucesso": round(float(taxa_sucesso * 100), 2) if taxa_sucesso else 0
                }
                for advogado, total_andamentos, taxa_sucesso in andamentos_por_advogado
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório"
        )

@router.get("/dashboard/", response_model=DashboardJuridicoResponse)
def dashboard_juridico(db: Session = Depends(get_db)):
    """
    Dashboard com métricas jurídicas completas
    """
    try:
        total_processos = db.query(Processo).count()
        processos_ativos = db.query(Processo).filter(Processo.status == "ativo").count()
        processos_encerrados = db.query(Processo).filter(Processo.status == "encerrado").count()
        processos_arquivados = db.query(Processo).filter(Processo.status == "arquivado").count()
        
        # Honorários totais
        honorarios_totais = sum(p.honorarios or 0 for p in db.query(Processo).all())
        honorarios_contratuais_totais = sum(p.honorarios_contratuais or 0 for p in db.query(Processo).all())
        
        # Processos por status
        processos_por_status = dict(db.query(
            Processo.status, 
            func.count(Processo.id)
        ).group_by(Processo.status).all())
        
        # Processos por tipo de ação
        processos_por_tipo = dict(db.query(
            Processo.tipo_acao,
            func.count(Processo.id)
        ).group_by(Processo.tipo_acao).all())
        
        # Audiências agendadas (próximos 30 dias)
        audiencias_proximas = db.query(Audiencia).filter(
            Audiencia.data_audiencia >= datetime.now(),
            Audiencia.data_audiencia <= datetime.now() + timedelta(days=30)
        ).count()
        
        # Processos com prazos próximos
        processos_prazo_proximo = db.query(Processo).filter(
            Processo.status == "ativo",
            Processo.data_prazo <= date.today() + timedelta(days=7),
            Processo.data_prazo >= date.today()
        ).count()
        
        return {
            "metricas_principais": {
                "total_processos": total_processos,
                "processos_ativos": processos_ativos,
                "processos_encerrados": processos_encerrados,
                "processos_arquivados": processos_arquivados,
                "honorarios_totais": honorarios_totais,
                "honorarios_contratuais": honorarios_contratuais_totais,
                "honorarios_devidos": max(0, honorarios_contratuais_totais - honorarios_totais)
            },
            "distribuicao": {
                "por_status": processos_por_status,
                "por_tipo_acao": processos_por_tipo
            },
            "alertas": {
                "audiencias_proximas": audiencias_proximas,
                "processos_prazo_proximo": processos_prazo_proximo,
                "taxa_encerramento": round((processos_encerrados / total_processos * 100) if total_processos > 0 else 0, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard jurídico: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar dashboard"
        )

@router.get("/previsao-honorarios/")
def previsao_honorarios(
    meses: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """
    Previsão de honorários para os próximos meses
    """
    try:
        hoje = date.today()
        previsao = {}
        
        for i in range(meses):
            mes_data = hoje.replace(day=1) + timedelta(days=32*i)
            mes_referencia = mes_data.replace(day=1)
            
            # Processos que provavelmente serão encerrados no mês
            processos_mes = db.query(Processo).filter(
                Processo.status == "ativo",
                Processo.data_prazo.between(mes_referencia, (mes_referencia + timedelta(days=32)).replace(day=1) - timedelta(days=1))
            ).all()
            
            honorarios_previstos = sum(p.honorarios_devidos or 0 for p in processos_mes)
            
            previsao[mes_referencia.strftime("%Y-%m")] = {
                "processos_previstos": len(processos_mes),
                "honorarios_previstos": honorarios_previstos
            }
        
        return {
            "periodo_meses": meses,
            "previsao": previsao,
            "total_honorarios_previstos": sum(mes["honorarios_previstos"] for mes in previsao.values())
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar previsão de honorários: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar previsão"
        )