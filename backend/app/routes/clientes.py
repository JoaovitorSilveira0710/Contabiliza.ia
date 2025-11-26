from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.database import get_db
from ..models.clientes import Cliente, Contrato
from ..schemas.clientes import (
    Cliente as ClienteSchema,
    ClienteCreate,
    ClienteUpdate,
    Contrato as ContratoSchema,
    ContratoCreate,
)

router = APIRouter(prefix="/clientes", tags=["clientes"])

# 📋 LISTAR TODOS OS CLIENTES
@router.get("/", response_model=List[ClienteSchema])
def listar_clientes(
    skip: int = 0, 
    limit: int = 100, 
    ativo: Optional[bool] = None,
    tipo_pessoa: Optional[str] = Query(None, description="F, J, fisica ou juridica"),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos os clientes com filtros opcionais
    """
    try:
        query = db.query(Cliente)
        
        # Conversor: "fisica" -> "F", "juridica" -> "J"
        tipo_pessoa_filtro = tipo_pessoa
        if tipo_pessoa:
            if tipo_pessoa.lower() == 'fisica':
                tipo_pessoa_filtro = 'F'
            elif tipo_pessoa.lower() == 'juridica':
                tipo_pessoa_filtro = 'J'
            elif tipo_pessoa not in ['F', 'J']:
                tipo_pessoa_filtro = None
        
        # Aplicar filtros
        if ativo is not None:
            query = query.filter(Cliente.ativo == ativo)
        
        if tipo_pessoa_filtro:
            query = query.filter(Cliente.tipo_pessoa == tipo_pessoa_filtro)
        
        if search:
            query = query.filter(
                (Cliente.nome_razao_social.ilike(f"%{search}%")) |
                (Cliente.cnpj_cpf.ilike(f"%{search}%")) |
                (Cliente.email.ilike(f"%{search}%"))
            )
        
        clientes = query.offset(skip).limit(limit).all()
        return clientes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar clientes: {str(e)}"
        )

# 👀 OBTER CLIENTE POR ID
@router.get("/{cliente_id}", response_model=ClienteSchema)
def obter_cliente(cliente_id: str, db: Session = Depends(get_db)):
    """
    Obtém um cliente específico pelo ID
    """
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return cliente
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter cliente: {str(e)}"
        )

# ➕ CRIAR NOVO CLIENTE
@router.post("/", response_model=ClienteSchema, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Cria um novo cliente
    """
    try:
        # Verificar se CNPJ/CPF já existe
        cliente_existente = db.query(Cliente).filter(Cliente.cnpj_cpf == cliente.cnpj_cpf).first()
        if cliente_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ/CPF já cadastrado"
            )
        
        # Conversor: garantir que tipo_pessoa seja F ou J
        cliente_data = cliente.model_dump()
        if cliente_data.get('tipo_pessoa'):
            if cliente_data['tipo_pessoa'].lower() == 'fisica':
                cliente_data['tipo_pessoa'] = 'F'
            elif cliente_data['tipo_pessoa'].lower() == 'juridica':
                cliente_data['tipo_pessoa'] = 'J'
        
        db_cliente = Cliente(**cliente_data)
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

# ✏️ ATUALIZAR CLIENTE (PATCH PARCIAL)
@router.patch("/{cliente_id}", response_model=ClienteSchema)
def atualizar_cliente_parcial(
    cliente_id: str,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente um cliente
    """
    try:
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not db_cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        update_data = cliente_update.model_dump(exclude_unset=True)
        
        # 🔥 CORREÇÃO: Verificar se há dados para atualizar
        if not update_data:
            return db_cliente
        
        if 'tipo_pessoa' in update_data:
            if update_data['tipo_pessoa'].lower() == 'fisica':
                update_data['tipo_pessoa'] = 'F'
            elif update_data['tipo_pessoa'].lower() == 'juridica':
                update_data['tipo_pessoa'] = 'J'
        
        if 'cnpj_cpf' in update_data:
            cliente_existente = db.query(Cliente).filter(
                Cliente.cnpj_cpf == update_data['cnpj_cpf'],
                Cliente.id != cliente_id
            ).first()
            if cliente_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CNPJ/CPF já cadastrado em outro cliente"
                )
        
        for key, value in update_data.items():
            setattr(db_cliente, key, value)
        
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

# 🗑️ EXCLUIR CLIENTE (ADICIONEI ESTA FUNÇÃO QUE FALTAVA)
@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cliente(cliente_id: str, db: Session = Depends(get_db)):
    """
    Exclui um cliente (soft delete - marca como inativo)
    """
    try:
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not db_cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Soft delete - marca como inativo em vez de excluir
        db_cliente.ativo = False
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir cliente: {str(e)}"
        )

# 📑 CONTRATOS DO CLIENTE
@router.get("/{cliente_id}/contratos", response_model=List[ContratoSchema])
def listar_contratos_cliente(cliente_id: str, db: Session = Depends(get_db)):
    """
    Lista todos os contratos de um cliente
    """
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        contratos = db.query(Contrato).filter(Contrato.cliente_id == cliente_id).all()
        return contratos
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar contratos: {str(e)}"
        )

# ➕ CRIAR CONTRATO PARA CLIENTE (FUNÇÃO ADICIONAL ÚTIL)
@router.post("/{cliente_id}/contratos", response_model=ContratoSchema, status_code=status.HTTP_201_CREATED)
def criar_contrato_cliente(
    cliente_id: str,
    contrato_data: ContratoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo contrato para o cliente
    """
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        # Usar schema ContratoCreate para validação e criação
        contrato_payload = contrato_data.model_dump()
        contrato_payload['cliente_id'] = cliente_id
        db_contrato = Contrato(**contrato_payload)
        db.add(db_contrato)
        db.commit()
        db.refresh(db_contrato)
        return db_contrato
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar contrato: {str(e)}"
        )