from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import logging

from ..models.database import get_db
from ..models.contabil import DRE, ObrigacaoAcessoria
from ..schemas.contabil import (
    DRE as DRESchema,
    DRECreate,
    DREUpdate,
    ObrigacaoAcessoria as ObrigacaoSchema,
    ObrigacaoAcessoriaCreate,
    ObrigacaoAcessoriaUpdate
)

router = APIRouter(prefix="/contabil", tags=["contabilidade"])
logger = logging.getLogger(__name__)

# 📊 DRE - DEMONSTRAÇÃO DO RESULTADO

@router.get("/dre/", response_model=List[DRESchema])
def listar_dres(
    cliente_id: Optional[str] = None,
    periodo: Optional[str] = None,  # 🔥 CORREÇÃO: mudado de mes_referencia para periodo (String)
    ano: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista DREs com filtros opcionais por cliente, período e ano
    """
    try:
        query = db.query(DRE)
        
        if cliente_id:
            query = query.filter(DRE.cliente_id == cliente_id)
        
        if periodo:
            query = query.filter(DRE.periodo == periodo)  # 🔥 CORREÇÃO: periodo em vez de mes_referencia
        
        if ano:
            # 🔥 CORREÇÃO: filtrar por ano no campo periodo (formato "YYYY-MM")
            query = query.filter(DRE.periodo.like(f"{ano}-%"))
        
        dres = query.order_by(DRE.periodo.desc()).offset(skip).limit(limit).all()
        return dres
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar DREs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar DREs"
        )

@router.get("/dre/{dre_id}", response_model=DRESchema)
def obter_dre(dre_id: str, db: Session = Depends(get_db)):
    """
    Obtém uma DRE específica pelo ID
    """
    try:
        dre = db.query(DRE).filter(DRE.id == dre_id).first()
        if not dre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DRE não encontrada"
            )
        return dre
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter DRE: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter DRE"
        )

@router.post("/dre/", response_model=DRESchema, status_code=status.HTTP_201_CREATED)
def criar_dre(dre: DRECreate, db: Session = Depends(get_db)):
    """
    Cria uma nova DRE
    """
    try:
        # Verificar se já existe DRE para o mesmo cliente e período
        dre_existente = db.query(DRE).filter(
            DRE.cliente_id == dre.cliente_id,
            DRE.periodo == dre.periodo  # 🔥 CORREÇÃO: periodo em vez de mes_referencia
        ).first()
        
        if dre_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma DRE para este cliente no período de referência"
            )
        
        db_dre = DRE(**dre.model_dump())
        
        # 🔥 CORREÇÃO: Chamar calcular_todos() se o método existir
        if hasattr(db_dre, 'calcular_todos'):
            db_dre.calcular_todos()
        
        db.add(db_dre)
        db.commit()
        db.refresh(db_dre)
        return db_dre
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao criar DRE: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar DRE"
        )

@router.patch("/dre/{dre_id}", response_model=DRESchema)
def atualizar_dre_parcial(
    dre_id: str,
    dre_update: DREUpdate, 
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente uma DRE
    """
    try:
        db_dre = db.query(DRE).filter(DRE.id == dre_id).first()
        if not db_dre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DRE não encontrada"
            )
        
        update_data = dre_update.model_dump(exclude_unset=True)
        
        # Verificar se há dados para atualizar
        if not update_data:
            return db_dre
        
        # Verificar unicidade se estiver atualizando período ou cliente
        if 'cliente_id' in update_data or 'periodo' in update_data:  # 🔥 CORREÇÃO: periodo
            novo_cliente_id = update_data.get('cliente_id', db_dre.cliente_id)
            novo_periodo = update_data.get('periodo', db_dre.periodo)  # 🔥 CORREÇÃO: periodo
            
            dre_existente = db.query(DRE).filter(
                DRE.cliente_id == novo_cliente_id,
                DRE.periodo == novo_periodo,  # 🔥 CORREÇÃO: periodo
                DRE.id != dre_id
            ).first()
            
            if dre_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma DRE para este cliente no período de referência"
                )
        
        for key, value in update_data.items():
            setattr(db_dre, key, value)
        
        # 🔥 CORREÇÃO: Chamar calcular_todos() se o método existir
        if hasattr(db_dre, 'calcular_todos'):
            db_dre.calcular_todos()
        
        db.commit()
        db.refresh(db_dre)
        return db_dre
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao atualizar DRE: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar DRE"
        )

@router.delete("/dre/{dre_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_dre(dre_id: str, db: Session = Depends(get_db)):
    """
    Exclui uma DRE
    """
    try:
        dre = db.query(DRE).filter(DRE.id == dre_id).first()
        if not dre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DRE não encontrada"
            )
        
        db.delete(dre)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao excluir DRE: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir DRE"
        )

# 📋 OBRIGAÇÕES ACESSÓRIAS

@router.get("/obrigacoes/", response_model=List[ObrigacaoSchema])
def listar_obrigacoes(
    cliente_id: Optional[str] = None,
    status: Optional[str] = Query(None, description="pendente, entregue ou atrasado"),
    periodicidade: Optional[str] = Query(None, description="mensal, trimestral ou anual"),
    data_vencimento_inicio: Optional[date] = None,
    data_vencimento_fim: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista obrigações acessórias com filtros avançados
    """
    try:
        query = db.query(ObrigacaoAcessoria)
        
        if cliente_id:
            query = query.filter(ObrigacaoAcessoria.cliente_id == cliente_id)
        
        if status:
            status_filtro = status.lower()
            if status_filtro in ['pendente', 'entregue', 'atrasado']:
                query = query.filter(ObrigacaoAcessoria.status == status_filtro)
        
        if periodicidade:
            query = query.filter(ObrigacaoAcessoria.periodicidade == periodicidade)
        
        if data_vencimento_inicio:
            query = query.filter(ObrigacaoAcessoria.data_vencimento >= data_vencimento_inicio)
        
        if data_vencimento_fim:
            query = query.filter(ObrigacaoAcessoria.data_vencimento <= data_vencimento_fim)
        
        obrigacoes = query.order_by(ObrigacaoAcessoria.data_vencimento.asc()).offset(skip).limit(limit).all()
        
        # 🔥 CORREÇÃO: Chamar atualizar_status_automatico() se o método existir
        for obrigacao in obrigacoes:
            if hasattr(obrigacao, 'atualizar_status_automatico'):
                obrigacao.atualizar_status_automatico()
        
        return obrigacoes
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar obrigações: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar obrigações"
        )

@router.get("/obrigacoes/{obrigacao_id}", response_model=ObrigacaoSchema)
def obter_obrigacao(obrigacao_id: str, db: Session = Depends(get_db)):
    """
    Obtém uma obrigação acessória específica pelo ID
    """
    try:
        obrigacao = db.query(ObrigacaoAcessoria).filter(ObrigacaoAcessoria.id == obrigacao_id).first()
        if not obrigacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obrigação não encontrada"
            )
        
        # 🔥 CORREÇÃO: Chamar atualizar_status_automatico() se o método existir
        if hasattr(obrigacao, 'atualizar_status_automatico'):
            obrigacao.atualizar_status_automatico()
        
        return obrigacao
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter obrigação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter obrigação"
        )

@router.post("/obrigacoes/", response_model=ObrigacaoSchema, status_code=status.HTTP_201_CREATED)
def criar_obrigacao(obrigacao: ObrigacaoAcessoriaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova obrigação acessória
    """
    try:
        db_obrigacao = ObrigacaoAcessoria(**obrigacao.model_dump())
        
        # 🔥 CORREÇÃO: Chamar atualizar_status_automatico() se o método existir
        if hasattr(db_obrigacao, 'atualizar_status_automatico'):
            db_obrigacao.atualizar_status_automatico()
        
        db.add(db_obrigacao)
        db.commit()
        db.refresh(db_obrigacao)
        return db_obrigacao
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao criar obrigação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar obrigação"
        )

@router.patch("/obrigacoes/{obrigacao_id}", response_model=ObrigacaoSchema)
def atualizar_obrigacao_parcial(
    obrigacao_id: str,
    obrigacao_update: ObrigacaoAcessoriaUpdate, 
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente uma obrigação acessória
    """
    try:
        db_obrigacao = db.query(ObrigacaoAcessoria).filter(ObrigacaoAcessoria.id == obrigacao_id).first()
        if not db_obrigacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obrigação não encontrada"
            )
        
        update_data = obrigacao_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return db_obrigacao
        
        for key, value in update_data.items():
            setattr(db_obrigacao, key, value)
        
        # 🔥 CORREÇÃO: Chamar atualizar_status_automatico() se o método existir
        if hasattr(db_obrigacao, 'atualizar_status_automatico'):
            db_obrigacao.atualizar_status_automatico()
        
        db.commit()
        db.refresh(db_obrigacao)
        return db_obrigacao
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao atualizar obrigação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar obrigação"
        )

@router.post("/obrigacoes/{obrigacao_id}/entregar", response_model=ObrigacaoSchema)
def marcar_obrigacao_entregue(
    obrigacao_id: str,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Marca uma obrigação como entregue
    """
    try:
        obrigacao = db.query(ObrigacaoAcessoria).filter(ObrigacaoAcessoria.id == obrigacao_id).first()
        if not obrigacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obrigação não encontrada"
            )
        
        obrigacao.status = "entregue"
        obrigacao.data_entrega = datetime.now().date()
        if observacoes:
            if obrigacao.observacoes:
                obrigacao.observacoes += f"\n--- Entregue em {datetime.now().strftime('%d/%m/%Y')} ---\n{observacoes}"
            else:
                obrigacao.observacoes = f"Entregue em {datetime.now().strftime('%d/%m/%Y')}: {observacoes}"
        
        db.commit()
        db.refresh(obrigacao)
        return obrigacao
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao marcar obrigação como entregue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao marcar obrigação como entregue"
        )

@router.delete("/obrigacoes/{obrigacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_obrigacao(obrigacao_id: str, db: Session = Depends(get_db)):
    """
    Exclui uma obrigação acessória
    """
    try:
        obrigacao = db.query(ObrigacaoAcessoria).filter(ObrigacaoAcessoria.id == obrigacao_id).first()
        if not obrigacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obrigação não encontrada"
            )
        
        db.delete(obrigacao)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao excluir obrigação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir obrigação"
        )

# 📈 RELATÓRIOS E ESTATÍSTICAS

@router.get("/relatorios/obrigacoes-pendentes")
def relatorio_obrigacoes_pendentes(
    dias_para_vencer: int = Query(7, description="Dias para considerar como 'próximo do vencimento'"),
    cliente_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Relatório de obrigações pendentes com alertas de vencimento
    """
    try:
        query = db.query(ObrigacaoAcessoria).filter(
            ObrigacaoAcessoria.status == "pendente"
        )
        
        if cliente_id:
            query = query.filter(ObrigacaoAcessoria.cliente_id == cliente_id)
        
        obrigacoes_pendentes = query.all()
        
        # Atualizar status de todas as obrigações
        for obrigacao in obrigacoes_pendentes:
            if hasattr(obrigacao, 'atualizar_status_automatico'):
                obrigacao.atualizar_status_automatico()
        
        obrigacoes_proximas_vencimento = [
            o for o in obrigacoes_pendentes 
            if hasattr(o, 'dias_para_vencer') and o.dias_para_vencer is not None and 0 <= o.dias_para_vencer <= dias_para_vencer
        ]
        obrigacoes_atrasadas = [
            o for o in obrigacoes_pendentes 
            if hasattr(o, 'esta_atrasada') and o.esta_atrasada
        ]
        
        return {
            "total_pendentes": len(obrigacoes_pendentes),
            "proximas_vencimento": len(obrigacoes_proximas_vencimento),
            "atrasadas": len(obrigacoes_atrasadas),
            "obrigacoes_proximas": [
                {
                    "id": o.id,
                    "descricao": o.descricao,
                    "cliente_id": o.cliente_id,
                    "data_vencimento": o.data_vencimento,
                    "dias_para_vencer": getattr(o, 'dias_para_vencer', None)
                } for o in obrigacoes_proximas_vencimento
            ],
            "obrigacoes_atrasadas": [
                {
                    "id": o.id,
                    "descricao": o.descricao,
                    "cliente_id": o.cliente_id,
                    "data_vencimento": o.data_vencimento,
                    "dias_atraso": abs(getattr(o, 'dias_para_vencer', 0)) if getattr(o, 'dias_para_vencer', 0) < 0 else 0
                } for o in obrigacoes_atrasadas
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório de obrigações: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório"
        )

@router.get("/relatorios/dre-consolidado")
def dre_consolidado(
    periodo: str = Query(..., description="Período no formato YYYY-MM"),  # 🔥 CORREÇÃO: periodo em vez de mes_referencia
    db: Session = Depends(get_db)
):
    """
    DRE consolidado de todos os clientes para um período específico
    """
    try:
        dres_periodo = db.query(DRE).filter(DRE.periodo == periodo).all()  # 🔥 CORREÇÃO: periodo
        
        if not dres_periodo:
            return {
                "periodo": periodo,
                "message": "Nenhuma DRE encontrada para o período",
                "total_clientes": 0,
                "receita_bruta_total": 0,
                "lucro_liquido_total": 0,
                "media_margem_lucro": 0
            }
        
        receita_bruta_total = sum(d.receita_bruta or 0 for d in dres_periodo)
        lucro_liquido_total = sum(d.lucro_liquido or 0 for d in dres_periodo)
        
        # Filtrar DREs com receita > 0 para cálculo de margens
        dres_com_receita = [d for d in dres_periodo if d.receita_bruta and d.receita_bruta > 0]
        media_margem = sum(d.margem_lucro or 0 for d in dres_com_receita) / len(dres_com_receita) if dres_com_receita else 0
        
        consolidado = {
            "periodo": periodo,
            "total_clientes": len(dres_periodo),
            "clientes_com_receita": len(dres_com_receita),
            "receita_bruta_total": receita_bruta_total,
            "lucro_liquido_total": lucro_liquido_total,
            "media_margem_lucro": round(media_margem, 2),
            "clientes_com_lucro": len([d for d in dres_periodo if d.lucro_liquido and d.lucro_liquido > 0]),
            "clientes_com_prejuizo": len([d for d in dres_periodo if d.lucro_liquido and d.lucro_liquido < 0]),
            "clientes_sem_movimentacao": len([d for d in dres_periodo if not d.receita_bruta or d.receita_bruta == 0])
        }
        
        return consolidado
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar DRE consolidado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório consolidado"
        )

# 🔄 OPERAÇÕES EM MASSA

@router.post("/obrigacoes/lote/")
def criar_obrigacoes_lote(
    obrigacoes: List[ObrigacaoAcessoriaCreate],
    db: Session = Depends(get_db)
):
    """
    Cria múltiplas obrigações em lote
    """
    try:
        obrigacoes_criadas = []
        
        for obrigacao_data in obrigacoes:
            db_obrigacao = ObrigacaoAcessoria(**obrigacao_data.model_dump())
            
            # 🔥 CORREÇÃO: Chamar atualizar_status_automatico() se o método existir
            if hasattr(db_obrigacao, 'atualizar_status_automatico'):
                db_obrigacao.atualizar_status_automatico()
                
            db.add(db_obrigacao)
            obrigacoes_criadas.append(db_obrigacao)
        
        db.commit()
        
        # Refresh para obter IDs gerados
        for obrigacao in obrigacoes_criadas:
            db.refresh(obrigacao)
        
        return {
            "message": f"{len(obrigacoes_criadas)} obrigações criadas com sucesso",
            "obrigacoes_criadas": obrigacoes_criadas
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao criar obrigações em lote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar obrigações em lote"
        )