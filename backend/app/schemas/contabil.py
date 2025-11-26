from pydantic import BaseModel, validator, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class DREBase(BaseModel):
    mes_referencia: date = Field(..., description="Mês de referência da DRE (primeiro dia do mês)")
    receita_bruta: float = Field(..., ge=0, description="Receita bruta total")
    deducoes: float = Field(default=0, ge=0, description="Deduções da receita bruta")
    custos: float = Field(default=0, ge=0, description="Custos dos produtos/serviços vendidos")
    despesas_operacionais: float = Field(default=0, ge=0, description="Despesas operacionais")
    despesas_nao_operacionais: float = Field(default=0, ge=0, description="Despesas não operacionais")

    @validator('mes_referencia')
    def validar_mes_referencia(cls, v):
        if v.day != 1:
            raise ValueError('mes_referencia deve ser o primeiro dia do mês')
        return v

    @validator('deducoes')
    def validar_deducoes(cls, v, values):
        if 'receita_bruta' in values and v > values['receita_bruta']:
            raise ValueError('Deduções não podem ser maiores que a receita bruta')
        return v

class DRECreate(DREBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str

class DREUpdate(BaseModel):
    receita_bruta: Optional[float] = Field(None, ge=0)
    deducoes: Optional[float] = Field(None, ge=0)
    custos: Optional[float] = Field(None, ge=0)
    despesas_operacionais: Optional[float] = Field(None, ge=0)
    despesas_nao_operacionais: Optional[float] = Field(None, ge=0)

class DRE(DREBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    data_criacao: datetime
    created_at: datetime
    updated_at: datetime

    # Properties para campos calculados
    @property
    def receita_liquida(self) -> float:
        return self.receita_bruta - self.deducoes

    @property
    def lucro_bruto(self) -> float:
        return self.receita_liquida - self.custos

    @property
    def lucro_operacional(self) -> float:
        return self.lucro_bruto - self.despesas_operacionais

    @property
    def lucro_liquido(self) -> float:
        return self.lucro_operacional - self.despesas_nao_operacionais

    @property
    def margem_lucro(self) -> float:
        if self.receita_liquida > 0:
            return (self.lucro_liquido / self.receita_liquida) * 100
        return 0.0

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class DRESummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    mes_referencia: date
    receita_bruta: float
    lucro_liquido: float
    margem_lucro: float

    model_config = ConfigDict(from_attributes=True)

class DREConsolidadoResponse(BaseModel):
    mes_referencia: date
    total_clientes: int
    receita_bruta_total: float
    lucro_liquido_total: float
    media_margem_lucro: float
    clientes_com_lucro: int
    clientes_com_prejuizo: int
    detalhes: List[DRESummary]

# Schemas para Obrigações Acessórias
class ObrigacaoAcessoriaBase(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=200, description="Descrição da obrigação")
    periodicidade: str = Field(
        ..., 
        pattern="^(mensal|trimestral|anual)$",
        description="Periodicidade da obrigação"
    )
    data_vencimento: date = Field(..., description="Data de vencimento")
    tipo: str = Field(
        ..., 
        pattern="^(fiscal|contabil|trabalhista|previdenciaria|societaria)$",
        description="Tipo da obrigação"
    )
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")

    @validator('data_vencimento')
    def validar_data_vencimento(cls, v):
        return v

class ObrigacaoAcessoriaCreate(ObrigacaoAcessoriaBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str

    @validator('data_vencimento')
    def validar_data_vencimento_criacao(cls, v):
        if v < date.today():
            raise ValueError('Data de vencimento não pode ser no passado para novas obrigações')
        return v

class ObrigacaoAcessoriaUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=3, max_length=200)
    data_vencimento: Optional[date] = None
    data_entrega: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(pendente|entregue|atrasado|cancelado)$")
    tipo: Optional[str] = Field(
        None, 
        pattern="^(fiscal|contabil|trabalhista|previdenciaria|societaria)$"
    )
    observacoes: Optional[str] = Field(None, max_length=1000)

    @validator('data_entrega')
    def validar_data_entrega(cls, v, values):
        if v and 'data_vencimento' in values and values['data_vencimento']:
            if v < values['data_vencimento']:
                raise ValueError('Data de entrega não pode ser anterior ao vencimento')
        return v

class ObrigacaoAcessoria(ObrigacaoAcessoriaBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    data_entrega: Optional[date] = Field(None, description="Data de entrega/encaminhamento")
    status: str = Field(
        default="pendente",
        pattern="^(pendente|entregue|atrasado|cancelado)$",
        description="Status da obrigação"
    )
    created_at: datetime
    updated_at: datetime

    # Properties para campos calculados
    @property
    def dias_para_vencer(self) -> Optional[int]:
        if self.data_vencimento:
            return (self.data_vencimento - date.today()).days
        return None

    @property
    def esta_atrasada(self) -> bool:
        return (self.status == 'pendente' and 
                self.data_vencimento and 
                self.data_vencimento < date.today())

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ObrigacaoAcessoriaSummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    descricao: str
    data_vencimento: date
    status: str
    dias_para_vencer: Optional[int]
    tipo: str

    model_config = ConfigDict(from_attributes=True)

# Schemas para Relatórios e Dashboard
class DashboardContabilResponse(BaseModel):
    metricas_principais: Dict[str, float]
    dre_ultimo_mes: Optional[DRESummary]
    obrigacoes_pendentes: int
    obrigacoes_proximas: int
    obrigacoes_atrasadas: int
    evolucao_receita: List[Dict[str, Any]]
    distribuicao_obrigacoes: Dict[str, int]

class RelatorioObrigacoesResponse(BaseModel):
    periodo: Dict[str, date]
    total_obrigacoes: int
    obrigacoes_pendentes: List[ObrigacaoAcessoriaSummary]
    obrigacoes_proximas: List[ObrigacaoAcessoriaSummary]
    obrigacoes_atrasadas: List[ObrigacaoAcessoriaSummary]
    estatisticas: Dict[str, int]

class PerformanceClienteResponse(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    nome_cliente: str
    dre_ultimo_mes: Optional[DRESummary]
    total_obrigacoes: int
    obrigacoes_pendentes: int
    obrigacoes_entregues: int
    performance: str  # excelente, boa, regular, critica

    model_config = ConfigDict(from_attributes=True)

# Schemas para Cálculos Automáticos
class CalculoDREAuto(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    mes_referencia: date
    lancamentos_receita: List[Dict[str, Any]] = Field(default_factory=list)
    lancamentos_despesa: List[Dict[str, Any]] = Field(default_factory=list)

class DREAutoCalculada(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    mes_referencia: date
    receita_bruta: float
    deducoes: float
    custos: float
    despesas_operacionais: float
    despesas_nao_operacionais: float
    receita_liquida: float
    lucro_bruto: float
    lucro_operacional: float
    lucro_liquido: float
    margem_lucro: float

# Schemas para Filtros e Consultas
class DREFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: Optional[str] = None
    mes_referencia: Optional[date] = None
    ano: Optional[int] = None
    receita_minima: Optional[float] = None
    receita_maxima: Optional[float] = None

class ObrigacaoFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pendente|entregue|atrasado|cancelado)$")
    tipo: Optional[str] = Field(
        None, 
        pattern="^(fiscal|contabil|trabalhista|previdenciaria|societaria)$"
    )
    data_vencimento_inicio: Optional[date] = None
    data_vencimento_fim: Optional[date] = None
    data_entrega_inicio: Optional[date] = None
    data_entrega_fim: Optional[date] = None

# Response Models para Listagens
class DREListResponse(BaseModel):
    items: List[DRE]
    total: int
    page: int
    size: int
    pages: int

class ObrigacaoListResponse(BaseModel):
    items: List[ObrigacaoAcessoria]
    total: int
    page: int
    size: int
    pages: int

# Schemas para Webhooks/Notificações
class ObrigacaoNotificacao(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    obrigacao_id: str
    cliente_nome: str
    descricao: str
    data_vencimento: date
    dias_para_vencer: int
    tipo: str
    prioridade: str  # alta, media, baixa

class DRENotificacao(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    cliente_nome: str
    mes_referencia: date
    lucro_liquido: float
    margem_lucro: float
    situacao: str  # excelente, boa, regular, critica