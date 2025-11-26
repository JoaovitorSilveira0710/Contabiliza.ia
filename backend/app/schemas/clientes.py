from pydantic import BaseModel, validator, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid
import re

class ClienteBase(BaseModel):
    nome_razao_social: str = Field(..., min_length=3, max_length=200, description="Nome ou razão social do cliente")
    cnpj_cpf: str = Field(..., min_length=11, max_length=18, description="CNPJ ou CPF do cliente")
    email: Optional[EmailStr] = Field(None, description="E-mail do cliente")
    telefone: Optional[str] = Field(None, min_length=10, max_length=20, description="Telefone do cliente")
    
    # Endereço detalhado
    cep: Optional[str] = Field(None, max_length=10, description="CEP")
    logradouro: Optional[str] = Field(None, max_length=200, description="Logradouro (rua, avenida)")
    numero: Optional[str] = Field(None, max_length=20, description="Número")
    complemento: Optional[str] = Field(None, max_length=100, description="Complemento")
    bairro: Optional[str] = Field(None, max_length=100, description="Bairro")
    cidade: Optional[str] = Field(None, max_length=100, description="Cidade")
    uf: Optional[str] = Field(None, min_length=2, max_length=2, description="UF (estado)")
    endereco: Optional[str] = Field(None, max_length=500, description="Endereço completo (compatibilidade)")
    
    tipo_pessoa: str = Field(..., pattern="^(F|J)$", description="Tipo de pessoa: F para Física, J para Jurídica")
    inscricao_estadual: Optional[str] = Field(None, max_length=20, description="Inscrição estadual")
    inscricao_municipal: Optional[str] = Field(None, max_length=20, description="Inscrição municipal")
    regime_tributario: Optional[str] = Field(
        None, 
        pattern="^(Simples Nacional|Lucro Presumido|Lucro Real|MEI)$",
        description="Regime tributário do cliente"
    )
    data_abertura: Optional[date] = Field(None, description="Data de abertura da empresa")
    atividade_principal: Optional[str] = Field(None, max_length=200, description="Atividade principal (CNAE)")

    @validator('uf')
    def validar_uf(cls, v):
        if v:
            ufs_validas = [
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
                'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
                'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ]
            if v.upper() not in ufs_validas:
                raise ValueError('UF inválida')
            return v.upper()
        return v

    @validator('cnpj_cpf')
    def validar_cnpj_cpf(cls, v, values):
        if 'tipo_pessoa' in values:
            if values['tipo_pessoa'] == 'J' and len(v) != 14:
                raise ValueError('CNPJ deve ter 14 dígitos para pessoa jurídica')
            elif values['tipo_pessoa'] == 'F' and len(v) != 11:
                raise ValueError('CPF deve ter 11 dígitos para pessoa física')
        
        # Remover caracteres não numéricos para validação
        v_clean = re.sub(r'\D', '', v)
        
        # Validação básica
        if values.get('tipo_pessoa') == 'J' and len(v_clean) != 14:
            raise ValueError('CNPJ inválido')
        elif values.get('tipo_pessoa') == 'F' and len(v_clean) != 11:
            raise ValueError('CPF inválido')
        
        return v_clean

    @validator('telefone')
    def validar_telefone(cls, v):
        if v is not None:
            v_clean = re.sub(r'\D', '', v)
            if len(v_clean) < 10 or len(v_clean) > 11:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome_razao_social: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    
    # Endereço detalhado
    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, min_length=2, max_length=2)
    endereco: Optional[str] = Field(None, max_length=500)
    
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    inscricao_municipal: Optional[str] = Field(None, max_length=20)
    regime_tributario: Optional[str] = Field(
        None, 
        pattern="^(Simples Nacional|Lucro Presumido|Lucro Real|MEI)$"
    )
    data_abertura: Optional[date] = None
    atividade_principal: Optional[str] = Field(None, max_length=200)
    ativo: Optional[bool] = None

class Cliente(ClienteBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    data_cadastro: datetime
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ClienteListResponse(BaseModel):
    items: List[Cliente]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)

class ClienteDashboardStats(BaseModel):
    total_clientes: int
    clientes_ativos: int
    clientes_inativos: int
    novos_este_mes: int
    distribuicao_regime: dict
    distribuicao_tipo: dict

# Schemas para Contratos
class ContratoBase(BaseModel):
    tipo_servico: str = Field(
        ..., 
        pattern="^(contabil|juridico|ambos)$",
        description="Tipo de serviço: contabil, juridico ou ambos"
    )
    valor_mensal: float = Field(..., gt=0, description="Valor mensal do contrato")
    data_inicio: date = Field(..., description="Data de início do contrato")
    data_termino: Optional[date] = Field(None, description="Data de término do contrato")
    dia_vencimento: int = Field(..., ge=1, le=31, description="Dia do vencimento mensal")
    status: str = Field(
        default="ativo",
        pattern="^(ativo|inativo|suspenso|cancelado)$",
        description="Status do contrato"
    )
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações do contrato")

    @validator('data_termino')
    def validar_data_termino(cls, v, values):
        if v and 'data_inicio' in values:
            if v <= values['data_inicio']:
                raise ValueError('Data de término deve ser posterior à data de início')
        return v

class ContratoCreate(ContratoBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str

class ContratoUpdate(BaseModel):
    tipo_servico: Optional[str] = Field(None, pattern="^(contabil|juridico|ambos)$")
    valor_mensal: Optional[float] = Field(None, gt=0)
    data_termino: Optional[date] = None
    dia_vencimento: Optional[int] = Field(None, ge=1, le=31)
    status: Optional[str] = Field(None, pattern="^(ativo|inativo|suspenso|cancelado)$")
    observacoes: Optional[str] = Field(None, max_length=1000)

class Contrato(ContratoBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

# Response Models
class ClienteWithContratos(Cliente):
    contratos: List[Contrato] = []

class ClienteSummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    nome_razao_social: str
    cnpj_cpf: str
    tipo_pessoa: str
    ativo: bool
    total_contratos: int
    total_servicos: int

    model_config = ConfigDict(from_attributes=True)