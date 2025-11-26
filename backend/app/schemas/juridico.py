from pydantic import BaseModel, validator, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

class ProcessoBase(BaseModel):
    numero_processo: str = Field(..., min_length=5, max_length=100, description="Número do processo judicial")
    vara: Optional[str] = Field(None, max_length=100, description="Vara/Órgão julgador")
    assunto: str = Field(..., min_length=5, max_length=200, description="Assunto/resumo do processo")
    data_distribuicao: Optional[date] = Field(None, description="Data de distribuição do processo")
    tipo_acao: Optional[str] = Field(
        None,
        pattern="^(civel|trabalhista|tributario|administrativo|consumerista|outros)$",
        description="Tipo da ação judicial"
    )
    valor_causa: Optional[float] = Field(None, ge=0, description="Valor da causa")
    honorarios: Optional[float] = Field(None, ge=0, description="Honorários já pagos")
    honorarios_contratuais: Optional[float] = Field(None, ge=0, description="Honorários contratados")
    parte_contraria: Optional[str] = Field(None, max_length=200, description="Nome da parte contrária")
    advogado_responsavel: Optional[str] = Field(None, max_length=100, description="Advogado responsável")
    data_prazo: Optional[date] = Field(None, description="Próximo prazo importante")
    observacoes: Optional[str] = Field(None, max_length=2000, description="Observações do processo")

    @validator('numero_processo')
    def validar_numero_processo(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Número do processo deve conter dígitos')
        return v

    @validator('data_distribuicao')
    def validar_data_distribuicao(cls, v):
        if v and v > date.today():
            raise ValueError('Data de distribuição não pode ser futura')
        return v

    @validator('data_prazo')
    def validar_data_prazo(cls, v, values):
        if v and 'data_distribuicao' in values and values['data_distribuicao']:
            if v < values['data_distribuicao']:
                raise ValueError('Data de prazo não pode ser anterior à distribuição')
        return v

    @validator('honorarios')
    def validar_honorarios(cls, v, values):
        if v and 'honorarios_contratuais' in values and values['honorarios_contratuais']:
            if v > values['honorarios_contratuais']:
                raise ValueError('Honorários pagos não podem ser maiores que os contratuais')
        return v

class ProcessoCreate(ProcessoBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str

class ProcessoUpdate(BaseModel):
    vara: Optional[str] = Field(None, max_length=100)
    assunto: Optional[str] = Field(None, min_length=5, max_length=200)
    status: Optional[str] = Field(
        None,
        pattern="^(ativo|encerrado|arquivado|suspenso)$",
        description="Status do processo"
    )
    valor_causa: Optional[float] = Field(None, ge=0)
    honorarios: Optional[float] = Field(None, ge=0)
    honorarios_contratuais: Optional[float] = Field(None, ge=0)
    parte_contraria: Optional[str] = Field(None, max_length=200)
    advogado_responsavel: Optional[str] = Field(None, max_length=100)
    data_prazo: Optional[date] = None
    observacoes: Optional[str] = Field(None, max_length=2000)

class Processo(ProcessoBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    status: str = Field(
        default="ativo",
        pattern="^(ativo|encerrado|arquivado|suspenso)$",
        description="Status do processo"
    )
    ultima_movimentacao: Optional[str] = Field(None, description="Última movimentação registrada")
    data_ultima_movimentacao: Optional[date] = Field(None, description="Data da última movimentação")
    data_criacao: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ProcessoSummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    numero_processo: str
    assunto: str
    status: str
    data_distribuicao: Optional[date]
    valor_causa: Optional[float]
    honorarios_devidos: float
    prazo_proximo: bool
    prazo_vencido: bool

    model_config = ConfigDict(from_attributes=True)

# Schemas para Andamentos Processuais
class AndamentoProcessualBase(BaseModel):
    descricao: str = Field(..., min_length=5, max_length=2000, description="Descrição do andamento")
    tipo: str = Field(
        ...,
        pattern="^(sentenca|despacho|audiencia|peticao|citacao|intimacao|outros)$",
        description="Tipo do andamento"
    )
    resultado: Optional[str] = Field(
        None,
        pattern="^(favoravel|desfavoravel|neutro|parcial)$",
        description="Resultado do andamento"
    )
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")
    usuario_responsavel: Optional[str] = Field(None, max_length=100, description="Usuário responsável")
    data_andamento: datetime = Field(default_factory=datetime.now, description="Data do andamento")

    @validator('data_andamento')
    def validar_data_andamento(cls, v):
        if v > datetime.now():
            raise ValueError('Data do andamento não pode ser futura')
        return v

class AndamentoProcessualCreate(AndamentoProcessualBase):
    # 🔥 CORREÇÃO: UUID como string
    processo_id: str

class AndamentoProcessualUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=5, max_length=2000)
    tipo: Optional[str] = Field(
        None,
        pattern="^(sentenca|despacho|audiencia|peticao|citacao|intimacao|outros)$"
    )
    resultado: Optional[str] = Field(
        None,
        pattern="^(favoravel|desfavoravel|neutro|parcial)$"
    )
    observacoes: Optional[str] = Field(None, max_length=1000)
    usuario_responsavel: Optional[str] = Field(None, max_length=100)
    data_andamento: Optional[datetime] = None

class AndamentoProcessual(AndamentoProcessualBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    processo_id: str
    created_at: datetime

    # Properties para campos calculados
    @property
    def e_favoravel(self) -> bool:
        return self.resultado == 'favoravel'

    @property
    def e_desfavoravel(self) -> bool:
        return self.resultado == 'desfavoravel'

    @property
    def dias_desde_andamento(self) -> int:
        return (datetime.now() - self.data_andamento).days

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class AndamentoProcessualSummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    data_andamento: datetime
    descricao: str
    tipo: str
    resultado: Optional[str]
    usuario_responsavel: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# Schemas para Audiências
class AudienciaBase(BaseModel):
    data_audiencia: datetime = Field(..., description="Data e hora da audiência")
    tipo: str = Field(
        ...,
        pattern="^(instrucao|conciliacao|julgamento|diligencia)$",
        description="Tipo de audiência"
    )
    local: Optional[str] = Field(None, max_length=200, description="Local da audiência")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")

    @validator('data_audiencia')
    def validar_data_audiencia(cls, v):
        if v < datetime.now():
            raise ValueError('Data da audiência não pode ser no passado')
        return v

class AudienciaCreate(AudienciaBase):
    # 🔥 CORREÇÃO: UUID como string
    processo_id: str

class AudienciaUpdate(BaseModel):
    data_audiencia: Optional[datetime] = None
    tipo: Optional[str] = Field(
        None,
        pattern="^(instrucao|conciliacao|julgamento|diligencia)$"
    )
    local: Optional[str] = Field(None, max_length=200)
    resultado: Optional[str] = Field(None, max_length=1000)
    comparecimento: Optional[bool] = None
    observacoes: Optional[str] = Field(None, max_length=1000)

class Audiencia(AudienciaBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    processo_id: str
    resultado: Optional[str] = Field(None, description="Resultado da audiência")
    comparecimento: Optional[bool] = Field(None, description="Cliente compareceu?")
    created_at: datetime
    updated_at: datetime

    # Properties para campos calculados
    @property
    def dias_para_audiencia(self) -> int:
        return max(0, (self.data_audiencia - datetime.now()).days)

    @property
    def audiencia_proxima(self) -> bool:
        return 0 <= self.dias_para_audiencia <= 7

    model_config = ConfigDict(from_attributes=True)

# Schemas para Dashboard Jurídico
class DashboardJuridicoResponse(BaseModel):
    metricas_principais: Dict[str, int]
    distribuicao: Dict[str, Dict[str, int]]
    alertas: Dict[str, int]
    processos_prazo_proximo: List[ProcessoSummary]
    audiencias_proximas: List[Audiencia]

class MetricaJuridica(BaseModel):
    nome: str
    valor: int
    variacao: float
    icone: str
    cor: str

# Schemas para Relatórios
class RelatorioProcessosAtivos(BaseModel):
    total_processos: int
    total_honorarios_estimados: float
    total_valor_causa: float
    processos_por_cliente: int
    processos_por_tipo: Dict[str, int]
    processos_prazo_proximo: int
    processos_prazo_vencido: int
    honorarios_devidos: float

class RelatorioPerformanceAdvogados(BaseModel):
    periodo: Dict[str, date]
    performance_advogados: List[Dict[str, Any]]

class RelatorioProcessosSemMovimentacao(BaseModel):
    dias_sem_movimentacao: int
    total_processos: int
    processos: List[ProcessoSummary]

# Schemas para Filtros e Consultas
class ProcessoFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ativo|encerrado|arquivado|suspenso)$")
    tipo_acao: Optional[str] = Field(
        None,
        pattern="^(civel|trabalhista|tributario|administrativo|consumerista|outros)$"
    )
    advogado_responsavel: Optional[str] = None
    data_distribuicao_inicio: Optional[date] = None
    data_distribuicao_fim: Optional[date] = None
    data_prazo_inicio: Optional[date] = None
    data_prazo_fim: Optional[date] = None
    valor_causa_minimo: Optional[float] = None
    valor_causa_maximo: Optional[float] = None

class AndamentoFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    processo_id: Optional[str] = None
    tipo: Optional[str] = Field(
        None,
        pattern="^(sentenca|despacho|audiencia|peticao|citacao|intimacao|outros)$"
    )
    resultado: Optional[str] = Field(
        None,
        pattern="^(favoravel|desfavoravel|neutro|parcial)$"
    )
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    usuario_responsavel: Optional[str] = None

# Response Models para Listagens
class ProcessoListResponse(BaseModel):
    items: List[Processo]
    total: int
    page: int
    size: int
    pages: int
    totais: Dict[str, Any]

class AndamentoListResponse(BaseModel):
    items: List[AndamentoProcessual]
    total: int
    page: int
    size: int
    pages: int

# Schemas para Operações Específicas
class EncerramentoProcesso(BaseModel):
    resultado: str = Field(..., description="Resultado do encerramento")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações do encerramento")

class AtualizacaoMovimentacao(BaseModel):
    descricao: str = Field(..., min_length=5, max_length=2000, description="Descrição da movimentação")
    tipo: str = Field(
        ...,
        pattern="^(sentenca|despacho|audiencia|peticao|citacao|intimacao|outros)$",
        description="Tipo da movimentação"
    )
    resultado: Optional[str] = Field(
        None,
        pattern="^(favoravel|desfavoravel|neutro|parcial)$"
    )

class RealizacaoAudiencia(BaseModel):
    resultado: str = Field(..., max_length=1000, description="Resultado da audiência")
    comparecimento: bool = Field(..., description="Cliente compareceu?")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")

# Schemas para Análises
class AnaliseProcesso(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    processo_id: str
    numero_processo: str
    tempo_tramitacao: Optional[int]
    total_andamentos: int
    andamentos_favoraveis: int
    andamentos_desfavoraveis: int
    situacao_prazos: str
    recomendacoes: List[str]

class PrevisaoHonorarios(BaseModel):
    periodo_meses: int
    previsao: Dict[str, Dict[str, Any]]
    total_honorarios_previstos: float

# Schemas para Webhooks/Notificações
class NotificacaoPrazoProcesso(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    processo_id: str
    numero_processo: str
    cliente_nome: str
    assunto: str
    data_prazo: date
    dias_para_prazo: int
    prioridade: str

class NotificacaoAudiencia(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    audiencia_id: str
    processo_numero: str
    cliente_nome: str
    data_audiencia: datetime
    dias_para_audiencia: int
    tipo: str
    local: Optional[str]