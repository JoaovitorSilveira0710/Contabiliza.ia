from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from ..models.database import get_db
from ..models.notas_fiscais import NotaFiscal, ItemNotaFiscal, EventoNotaFiscal
from ..models.clientes import Cliente
from ..schemas.notas_fiscais import (
    NotaFiscal as NotaFiscalSchema,
    NotaFiscalCreate,
    NotaFiscalUpdate,
    ItemNotaFiscal as ItemNotaFiscalSchema,
    EventoNotaFiscal as EventoNotaFiscalSchema,
    BuscaNotasFiscais,
    ImportacaoNotasResponse,
    DashboardNotasFiscaisResponse
)
from ..services.nfe_service import nfe_service, NFeServiceError

router = APIRouter(prefix="/notas-fiscais", tags=["notas-fiscais"])
logger = logging.getLogger(__name__)

# 🧾 NOTAS FISCAIS

@router.get("/", response_model=List[NotaFiscalSchema])
def listar_notas_fiscais(
    cliente_id: Optional[str] = None,
    tipo: Optional[str] = Query(None, regex="^(entrada|saida|servico)$"),
    situacao: Optional[str] = Query(None, regex="^(autorizada|cancelada|denegada|rejeitada|pendente)$"),
    modelo: Optional[str] = Query(None, regex="^(nfe|nfce|nfse)$"),
    data_emissao_inicio: Optional[date] = None,
    data_emissao_fim: Optional[date] = None,
    data_autorizacao_inicio: Optional[date] = None,
    data_autorizacao_fim: Optional[date] = None,
    valor_minimo: Optional[float] = None,
    valor_maximo: Optional[float] = None,
    cnpj_emitente: Optional[str] = None,
    cnpj_destinatario: Optional[str] = None,
    municipio: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista notas fiscais com filtros avançados
    """
    try:
        query = db.query(NotaFiscal)
        
        # Aplicar filtros
        if cliente_id:
            query = query.filter(NotaFiscal.cliente_id == cliente_id)
        
        if tipo:
            query = query.filter(NotaFiscal.tipo == tipo)
        
        if situacao:
            query = query.filter(NotaFiscal.situacao == situacao)
        
        if modelo:
            query = query.filter(NotaFiscal.modelo == modelo)
        
        if data_emissao_inicio:
            query = query.filter(NotaFiscal.data_emissao >= data_emissao_inicio)
        
        if data_emissao_fim:
            query = query.filter(NotaFiscal.data_emissao <= data_emissao_fim)
        
        if data_autorizacao_inicio:
            query = query.filter(NotaFiscal.data_autorizacao >= data_autorizacao_inicio)
        
        if data_autorizacao_fim:
            query = query.filter(NotaFiscal.data_autorizacao <= data_autorizacao_fim)
        
        if valor_minimo is not None:
            query = query.filter(NotaFiscal.valor_total >= valor_minimo)
        
        if valor_maximo is not None:
            query = query.filter(NotaFiscal.valor_total <= valor_maximo)
        
        if cnpj_emitente:
            query = query.filter(NotaFiscal.cnpj_emitente.ilike(f"%{cnpj_emitente}%"))
        
        if cnpj_destinatario:
            query = query.filter(NotaFiscal.cnpj_destinatario.ilike(f"%{cnpj_destinatario}%"))
        
        if municipio:
            query = query.filter(NotaFiscal.municipio.ilike(f"%{municipio}%"))
        
        notas = query.order_by(NotaFiscal.data_emissao.desc()).offset(skip).limit(limit).all()
        return notas
        
    except Exception as e:
        logger.error(f"Erro ao listar notas fiscais: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar notas fiscais"
        )

@router.get("/{nota_id}", response_model=NotaFiscalSchema)
def obter_nota_fiscal(nota_id: str, db: Session = Depends(get_db)):
    """
    Obtém uma nota fiscal específica pelo ID
    """
    try:
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        return nota
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter nota fiscal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter nota fiscal"
        )

@router.post("/", response_model=NotaFiscalSchema, status_code=status.HTTP_201_CREATED)
def criar_nota_fiscal(nota: NotaFiscalCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova nota fiscal
    """
    try:
        # Verificar se chave de acesso já existe (se fornecida)
        if nota.chave_acesso:
            nota_existente = db.query(NotaFiscal).filter(
                NotaFiscal.chave_acesso == nota.chave_acesso
            ).first()
            
            if nota_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chave de acesso já cadastrada"
                )
        
        # Verificar se cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == nota.cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente não encontrado"
            )
        
        # ✅ CORREÇÃO: usar model_dump() em vez de dict()
        db_nota = NotaFiscal(**nota.model_dump())
        
        # Se for autorizada, definir data de autorização
        if nota.situacao == "autorizada" and not nota.data_autorizacao:
            db_nota.data_autorizacao = datetime.now()
        
        db.add(db_nota)
        db.commit()
        db.refresh(db_nota)
        return db_nota
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar nota fiscal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar nota fiscal"
        )

@router.post("/emitir", response_model=NotaFiscalSchema, status_code=status.HTTP_201_CREATED)
async def emitir_nota_fiscal(
    nota: NotaFiscalCreate,
    itens: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
):
    """
    🆕 EMITE uma nova NFe através da SEFAZ
    
    Fluxo:
    1. Valida dados da nota
    2. Gera chave de acesso
    3. Monta XML
    4. Assina digitalmente (simulado)
    5. Transmite para SEFAZ (simulado)
    6. Armazena no banco
    """
    try:
        # Verificar se cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == nota.cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente não encontrado"
            )
        
        # Preparar dados para emissão
        dados_emissao = nota.model_dump()
        dados_emissao['data_emissao'] = datetime.now()
        
        # Emitir NFe através do serviço
        resultado = await nfe_service.emitir_nfe(dados_emissao, itens)
        
        if not resultado['sucesso']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado.get('mensagem', 'Erro ao emitir nota')
            )
        
        # Criar nota no banco com dados da autorização
        nota_data = nota.model_dump()
        nota_data['chave_acesso'] = resultado['chave_acesso']
        nota_data['situacao'] = 'autorizada'
        nota_data['data_autorizacao'] = resultado['data_autorizacao']
        
        db_nota = NotaFiscal(**nota_data)
        
        db.add(db_nota)
        db.flush()  # Gerar ID antes de criar evento
        
        # Criar evento de autorização
        evento = EventoNotaFiscal(
            nota_fiscal_id=db_nota.id,
            tipo_evento="autorizacao",
            numero_sequencial=1,
            data_evento=resultado['data_autorizacao'],
            protocolo=resultado['protocolo'],
            descricao="NFe autorizada pela SEFAZ"
        )
        db.add(evento)
        
        db.commit()
        db.refresh(db_nota)
        
        logger.info(f"✅ NFe emitida com sucesso - Chave: {resultado['chave_acesso']}")
        return db_nota
        
    except HTTPException:
        raise
    except NFeServiceError as e:
        db.rollback()
        logger.error(f"❌ Erro no serviço de NFe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao emitir NFe: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro inesperado ao emitir NFe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao emitir nota fiscal"
        )

@router.patch("/{nota_id}", response_model=NotaFiscalSchema)
def atualizar_nota_fiscal_parcial(
    nota_id: str,
    nota_update: NotaFiscalUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente uma nota fiscal
    """
    try:
        db_nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not db_nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        # ✅ CORREÇÃO: usar model_dump() em vez de dict()
        update_data = nota_update.model_dump(exclude_unset=True)
        
        # Verificar unicidade se estiver atualizando chave de acesso
        if 'chave_acesso' in update_data:
            nota_existente = db.query(NotaFiscal).filter(
                NotaFiscal.chave_acesso == update_data['chave_acesso'],
                NotaFiscal.id != nota_id
            ).first()
            
            if nota_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chave de acesso já cadastrada em outra nota"
                )
        
        for key, value in update_data.items():
            setattr(db_nota, key, value)
        
        db.commit()
        db.refresh(db_nota)
        return db_nota
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar nota fiscal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar nota fiscal"
        )

@router.post("/{nota_id}/autorizar", response_model=NotaFiscalSchema)
def autorizar_nota_fiscal(
    nota_id: str,
    db: Session = Depends(get_db)
):
    """
    Marca uma nota fiscal como autorizada
    """
    try:
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        # Gerar protocolo automático se não tiver
        import random
        protocolo = f"NFe{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        nota.situacao = "autorizada"
        nota.data_autorizacao = datetime.now()
        
        # Criar evento de autorização
        evento = EventoNotaFiscal(
            nota_fiscal_id=nota_id,
            tipo_evento="autorizacao",
            numero_sequencial=1,
            data_evento=datetime.now(),
            protocolo=protocolo,
            descricao="Nota fiscal autorizada"
        )
        db.add(evento)
        
        db.commit()
        db.refresh(nota)
        
        logger.info(f"✅ Nota {nota_id} autorizada - Protocolo: {protocolo}")
        return nota
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao autorizar nota fiscal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao autorizar nota fiscal"
        )

@router.post("/{nota_id}/cancelar", response_model=NotaFiscalSchema)
def cancelar_nota_fiscal(
    nota_id: str,
    justificativa: Optional[str] = "Cancelamento solicitado pelo cliente",
    db: Session = Depends(get_db)
):
    """
    Cancela uma nota fiscal
    """
    try:
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        if nota.situacao != "autorizada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas notas autorizadas podem ser canceladas"
            )
        
        # Gerar protocolo de cancelamento
        import random
        protocolo_cancelamento = f"CANC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        nota.situacao = "cancelada"
        
        # Criar evento de cancelamento
        evento = EventoNotaFiscal(
            nota_fiscal_id=nota_id,
            tipo_evento="cancelamento",
            numero_sequencial=2,
            data_evento=datetime.now(),
            protocolo=protocolo_cancelamento,
            justificativa=justificativa,
            descricao="Nota fiscal cancelada"
        )
        db.add(evento)
        
        db.commit()
        db.refresh(nota)
        
        logger.info(f"✅ Nota {nota_id} cancelada - Protocolo: {protocolo_cancelamento}")
        return nota
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao cancelar nota fiscal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cancelar nota fiscal"
        )

@router.post("/{nota_id}/cancelar-sefaz")
async def cancelar_nota_fiscal_sefaz(
    nota_id: str,
    justificativa: str,
    db: Session = Depends(get_db)
):
    """
    🆕 Cancela uma NFe na SEFAZ
    """
    try:
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        if nota.situacao != "autorizada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas notas autorizadas podem ser canceladas"
            )
        
        if not nota.chave_acesso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nota sem chave de acesso"
            )
        
        # Buscar protocolo de autorização
        evento_autorizacao = db.query(EventoNotaFiscal).filter(
            EventoNotaFiscal.nota_fiscal_id == nota_id,
            EventoNotaFiscal.tipo_evento == "autorizacao"
        ).first()
        
        protocolo_autorizacao = evento_autorizacao.protocolo if evento_autorizacao else ""
        
        # Cancelar na SEFAZ
        resultado = await nfe_service.cancelar_nfe(
            nota.chave_acesso,
            protocolo_autorizacao,
            justificativa
        )
        
        if resultado['sucesso']:
            # Atualizar nota
            nota.situacao = "cancelada"
            
            # Criar evento de cancelamento
            evento = EventoNotaFiscal(
                nota_fiscal_id=nota_id,
                tipo_evento="cancelamento",
                numero_sequencial=2,
                data_evento=resultado['data_cancelamento'],
                protocolo=resultado['protocolo_cancelamento'],
                justificativa=justificativa,
                descricao="NFe cancelada na SEFAZ"
            )
            db.add(evento)
            
            db.commit()
            db.refresh(nota)
            
            return {
                "sucesso": True,
                "mensagem": "NFe cancelada com sucesso na SEFAZ",
                "nota": nota,
                "protocolo": resultado['protocolo_cancelamento']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao cancelar na SEFAZ"
            )
            
    except HTTPException:
        raise
    except NFeServiceError as e:
        logger.error(f"❌ Erro no cancelamento SEFAZ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro no cancelamento: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao cancelar nota: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cancelar nota"
        )

@router.get("/{nota_id}/consultar-status")
async def consultar_status_nota(nota_id: str, db: Session = Depends(get_db)):
    """
    🆕 Consulta status da NFe na SEFAZ
    """
    try:
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        if not nota.chave_acesso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nota sem chave de acesso"
            )
        
        # Consultar na SEFAZ
        resultado = await nfe_service.consultar_status_nfe(nota.chave_acesso)
        
        return {
            "nota_id": nota_id,
            "chave_acesso": nota.chave_acesso,
            "status_sefaz": resultado,
            "status_local": nota.situacao
        }
        
    except HTTPException:
        raise
    except NFeServiceError as e:
        logger.error(f"❌ Erro na consulta SEFAZ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro na consulta: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Erro ao consultar status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar status"
        )

@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_nota_fiscal(nota_id: str, db: Session = Depends(get_db)):
    """
    Exclui uma nota fiscal
    """
    try:
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        db.delete(nota)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao excluir nota fiscal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir nota fiscal"
        )

# 📦 ITENS DA NOTA FISCAL

@router.get("/{nota_id}/itens", response_model=List[ItemNotaFiscalSchema])
def listar_itens_nota(nota_id: str, db: Session = Depends(get_db)):
    """
    Lista itens de uma nota fiscal
    """
    try:
        itens = db.query(ItemNotaFiscal).filter(
            ItemNotaFiscal.nota_fiscal_id == nota_id
        ).order_by(ItemNotaFiscal.numero_item.asc()).all()
        return itens
        
    except Exception as e:
        logger.error(f"Erro ao listar itens da nota: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar itens da nota"
        )

@router.post("/{nota_id}/itens", response_model=ItemNotaFiscalSchema)
def adicionar_item_nota(
    nota_id: str,
    item: ItemNotaFiscalSchema,
    db: Session = Depends(get_db)
):
    """
    Adiciona um item a uma nota fiscal
    """
    try:
        # Verificar se nota existe
        nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
        if not nota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada"
            )
        
        # ✅ CORREÇÃO: usar model_dump() em vez de dict()
        db_item = ItemNotaFiscal(nota_fiscal_id=nota_id, **item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao adicionar item à nota: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao adicionar item à nota"
        )

# 🔄 BUSCA E IMPORTACAO

@router.post("/buscar", response_model=ImportacaoNotasResponse)
def buscar_notas_fiscais(
    busca: BuscaNotasFiscais,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Inicia busca de notas fiscais na SEFAZ
    """
    try:
        # Verificar se cliente existe
        cliente = db.query(Cliente).filter(Cliente.cnpj_cpf == busca.cnpj).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente não encontrado para o CNPJ informado"
            )
        
        # Em produção, aqui integraria com API da SEFAZ
        background_tasks.add_task(
            simular_busca_sefaz,
            cliente.id,
            busca.cnpj,
            busca.data_inicio,
            busca.data_fim,
            busca.tipo,
            db
        )
        
        return {
            "message": "Busca de notas fiscais iniciada",
            "cliente": cliente.nome_razao_social,
            "cnpj": busca.cnpj,
            "periodo": {
                "inicio": busca.data_inicio,
                "fim": busca.data_fim
            },
            "tipo": busca.tipo,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar notas fiscais: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar notas fiscais"
        )

@router.post("/importar-xml", response_model=ImportacaoNotasResponse)
async def importar_notas_xml(
    arquivos: List[UploadFile] = File(...),
    cliente_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Importa notas fiscais a partir de arquivos XML
    """
    try:
        notas_importadas = 0
        notas_com_erro = 0
        
        for arquivo in arquivos:
            if not arquivo.filename.lower().endswith('.xml'):
                notas_com_erro += 1
                continue
            
            try:
                # Ler conteúdo do XML
                conteudo = await arquivo.read()
                xml_data = conteudo.decode('utf-8')
                
                # Em produção, aqui faria o parsing do XML
                # Por enquanto simulamos a importação
                nota_data = parse_xml_nota_fiscal(xml_data, cliente_id)
                
                if nota_data:
                    # Verificar se nota já existe
                    nota_existente = db.query(NotaFiscal).filter(
                        NotaFiscal.chave_acesso == nota_data["chave_acesso"]
                    ).first()
                    
                    if not nota_existente:
                        nova_nota = NotaFiscal(**nota_data)
                        db.add(nova_nota)
                        notas_importadas += 1
                    else:
                        notas_com_erro += 1
                else:
                    notas_com_erro += 1
                    
            except Exception as e:
                notas_com_erro += 1
                logger.error(f"Erro ao importar {arquivo.filename}: {str(e)}")
        
        if notas_importadas > 0:
            db.commit()
        
        return {
            "message": "Importação de XML concluída",
            "notas_importadas": notas_importadas,
            "notas_com_erro": notas_com_erro,
            "total_arquivos": len(arquivos)
        }
        
    except Exception as e:
        logger.error(f"Erro ao importar notas XML: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao importar notas XML"
        )

def parse_xml_nota_fiscal(xml_content: str, cliente_id: Optional[str] = None) -> Optional[Dict]:
    """
    Função para parsear XML de nota fiscal (simulação)
    Em produção, usar biblioteca como nfelib ou similar
    """
    # Simulação - em produção faria parsing real do XML
    try:
        # Extrair dados do XML (simulação)
        return {
            "cliente_id": cliente_id,
            "numero": "12345",
            "chave_acesso": "35210410898409000174550010000012341001234567",
            "tipo": "saida",
            "modelo": "nfe",
            "data_emissao": datetime.now() - timedelta(days=5),
            "valor_total": 2500.00,
            "situacao": "autorizada",
            "cnpj_emitente": "10898409000174",
            "cnpj_destinatario": "12345678000195",
            "municipio": "São Paulo"
        }
    except Exception as e:
        logger.error(f"Erro ao parsear XML: {str(e)}")
        return None

def simular_busca_sefaz(cliente_id: str, cnpj: str, data_inicio: date, data_fim: date, tipo: str, db: Session):
    """
    Função de simulação de busca na SEFAZ
    """
    try:
        import time
        time.sleep(3)  # Simula processamento
        
        # Notas de exemplo (em produção viriam da SEFAZ)
        notas_exemplo = [
            {
                "cliente_id": cliente_id,
                "numero": "12345",
                "chave_acesso": "35210410898409000174550010000012341001234567",
                "tipo": "saida",
                "modelo": "nfe",
                "data_emissao": datetime.now() - timedelta(days=5),
                "valor_total": 2500.00,
                "situacao": "autorizada",
                "cnpj_emitente": cnpj,
                "cnpj_destinatario": "12345678000195",
                "nome_destinatario": "Empresa Cliente Exemplo",
                "municipio": "São Paulo"
            },
            {
                "cliente_id": cliente_id,
                "numero": "12346",
                "chave_acesso": "35210410898409000174550010000012351001234568",
                "tipo": "entrada",
                "modelo": "nfe",
                "data_emissao": datetime.now() - timedelta(days=3),
                "valor_total": 1800.00,
                "situacao": "autorizada",
                "cnpj_emitente": "98765432000101",
                "cnpj_destinatario": cnpj,
                "nome_emitente": "Fornecedor Exemplo Ltda",
                "municipio": "Rio de Janeiro"
            }
        ]
        
        notas_importadas = 0
        for nota_data in notas_exemplo:
            # Verificar se nota já existe
            nota_existente = db.query(NotaFiscal).filter(
                NotaFiscal.chave_acesso == nota_data["chave_acesso"]
            ).first()
            
            if not nota_existente:
                nova_nota = NotaFiscal(**nota_data)
                db.add(nova_nota)
                notas_importadas += 1
        
        if notas_importadas > 0:
            db.commit()
            logger.info(f"✅ {notas_importadas} notas importadas para cliente {cliente_id}")
        else:
            logger.info(f"ℹ️ Nenhuma nova nota encontrada para cliente {cliente_id}")
            
    except Exception as e:
        logger.error(f"Erro na simulação SEFAZ: {str(e)}")

# 📊 RELATÓRIOS E ESTATÍSTICAS

@router.get("/relatorios/consolidado")
def relatorio_consolidado(
    data_inicio: date,
    data_fim: date,
    cliente_id: Optional[str] = None,
    tipo: Optional[str] = None,
    modelo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Relatório consolidado de notas fiscais
    """
    try:
        query = db.query(NotaFiscal).filter(
            NotaFiscal.data_emissao.between(data_inicio, data_fim)
        )
        
        if cliente_id:
            query = query.filter(NotaFiscal.cliente_id == cliente_id)
        
        if tipo:
            query = query.filter(NotaFiscal.tipo == tipo)
        
        if modelo:
            query = query.filter(NotaFiscal.modelo == modelo)
        
        notas = query.all()
        
        # Cálculos consolidados
        total_entradas = sum(n.valor_total for n in notas if n.tipo == "entrada")
        total_saidas = sum(n.valor_total for n in notas if n.tipo == "saida")
        total_servicos = sum(n.valor_total for n in notas if n.tipo == "servico")
        
        # Por situação
        notas_autorizadas = [n for n in notas if n.situacao == "autorizada"]
        notas_canceladas = [n for n in notas if n.situacao == "cancelada"]
        
        # Por modelo
        nfes = [n for n in notas if n.modelo == "nfe"]
        nfces = [n for n in notas if n.modelo == "nfce"]
        nfses = [n for n in notas if n.modelo == "nfse"]
        
        return {
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            },
            "totais": {
                "notas": len(notas),
                "valor_total": sum(n.valor_total for n in notas),
                "entradas": total_entradas,
                "saidas": total_saidas,
                "servicos": total_servicos,
                "saldo": total_entradas - total_saidas
            },
            "distribuicao": {
                "por_tipo": {
                    "entrada": len([n for n in notas if n.tipo == "entrada"]),
                    "saida": len([n for n in notas if n.tipo == "saida"]),
                    "servico": len([n for n in notas if n.tipo == "servico"])
                },
                "por_situacao": {
                    "autorizada": len(notas_autorizadas),
                    "cancelada": len(notas_canceladas),
                    "denegada": len([n for n in notas if n.situacao == "denegada"]),
                    "rejeitada": len([n for n in notas if n.situacao == "rejeitada"])
                },
                "por_modelo": {
                    "nfe": len(nfes),
                    "nfce": len(nfces),
                    "nfse": len(nfses)
                }
            },
            "metricas": {
                "valor_medio_nota": sum(n.valor_total for n in notas) / len(notas) if notas else 0,
                "taxa_cancelamento": (len(notas_canceladas) / len(notas) * 100) if notas else 0,
                "dias_emissao_autorizacao": sum((n.data_autorizacao - n.data_emissao).days for n in notas_autorizadas if n.data_autorizacao) / len(notas_autorizadas) if notas_autorizadas else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório consolidado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório"
        )

@router.get("/dashboard/", response_model=DashboardNotasFiscaisResponse)
def dashboard_notas_fiscais(
    periodo: str = Query("mensal", regex="^(mensal|trimestral|anual)$"),
    db: Session = Depends(get_db)
):
    """
    Dashboard com métricas de notas fiscais
    """
    try:
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
        total_notas = db.query(NotaFiscal).count()
        notas_periodo = db.query(NotaFiscal).filter(NotaFiscal.data_emissao >= data_inicio).all()
        
        total_valor_periodo = sum(n.valor_total for n in notas_periodo)
        media_diaria = total_valor_periodo / ((hoje.date() - data_inicio).days + 1)
        
        # Notas por tipo
        notas_por_tipo = dict(db.query(
            NotaFiscal.tipo, 
            func.count(NotaFiscal.id)
        ).group_by(NotaFiscal.tipo).all())
        
        # Notas por situação
        notas_por_situacao = dict(db.query(
            NotaFiscal.situacao, 
            func.count(NotaFiscal.id)
        ).group_by(NotaFiscal.situacao).all())
        
        # Notas por modelo
        notas_por_modelo = dict(db.query(
            NotaFiscal.modelo, 
            func.count(NotaFiscal.id)
        ).group_by(NotaFiscal.modelo).all())
        
        # Top clientes (por valor de notas)
        top_clientes = db.query(
            Cliente.nome_razao_social,
            func.sum(NotaFiscal.valor_total).label('total')
        ).join(NotaFiscal, NotaFiscal.cliente_id == Cliente.id).filter(
            NotaFiscal.data_emissao >= data_inicio
        ).group_by(Cliente.id, Cliente.nome_razao_social).order_by(
            func.sum(NotaFiscal.valor_total).desc()
        ).limit(5).all()
        
        return {
            "periodo": periodo,
            "data_inicio": data_inicio,
            "metricas_principais": {
                "total_notas": total_notas,
                "notas_periodo": len(notas_periodo),
                "valor_total_periodo": total_valor_periodo,
                "media_diaria": media_diaria,
                "valor_medio_nota": total_valor_periodo / len(notas_periodo) if notas_periodo else 0
            },
            "distribuicao": {
                "por_tipo": notas_por_tipo,
                "por_situacao": notas_por_situacao,
                "por_modelo": notas_por_modelo
            },
            "top_clientes": [
                {"nome": nome, "total_notas": float(total)} for nome, total in top_clientes
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar dashboard"
        )

@router.get("/estatisticas/mensais")
def estatisticas_mensais(
    ano: int,
    cliente_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Estatísticas mensais de notas fiscais
    """
    try:
        estatisticas = {}
        
        for mes in range(1, 13):
            data_inicio = date(ano, mes, 1)
            data_fim = (data_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            query = db.query(NotaFiscal).filter(
                NotaFiscal.data_emissao.between(data_inicio, data_fim)
            )
            
            if cliente_id:
                query = query.filter(NotaFiscal.cliente_id == cliente_id)
            
            notas_mes = query.all()
            
            estatisticas[data_inicio.strftime("%Y-%m")] = {
                "total_notas": len(notas_mes),
                "valor_total": sum(n.valor_total for n in notas_mes),
                "entradas": sum(n.valor_total for n in notas_mes if n.tipo == "entrada"),
                "saidas": sum(n.valor_total for n in notas_mes if n.tipo == "saida"),
                "servicos": sum(n.valor_total for n in notas_mes if n.tipo == "servico"),
                "notas_autorizadas": len([n for n in notas_mes if n.situacao == "autorizada"]),
                "notas_canceladas": len([n for n in notas_mes if n.situacao == "cancelada"])
            }
        
        return {
            "ano": ano,
            "estatisticas": estatisticas,
            "total_ano": {
                "notas": sum(mes["total_notas"] for mes in estatisticas.values()),
                "valor": sum(mes["valor_total"] for mes in estatisticas.values())
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas mensais: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar estatísticas"
        )