from pydantic import BaseModel, validator, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

class LancamentoFinanceiroBase(BaseModel):
    tipo: str = Field(
        ..., 
        pattern="^(receita|despesa)$",
        description="Tipo do lançamento: receita ou despesa"
    )
    descricao: str = Field(..., min_length=3, max_length=200, description="Descrição do lançamento")
    valor: float = Field(..., gt=0, description="Valor do lançamento")
    data_vencimento: date = Field(..., description="Data de vencimento")
    categoria: str = Field(
        ..., 
        pattern="^(honorarios|impostos|folha_pagamento|aluguel|telefonia|material|servicos|outros)$",
        description="Categoria do lançamento"
    )
    forma_pagamento: Optional[str] = Field(
        None,
        pattern="^(dinheiro|pix|transferencia|cartao_credito|cartao_debito|boleto)$",
        description="Forma de pagamento"
    )
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")

    @validator('data_vencimento')
    def validar_data_vencimento(cls, v):
        if v < date.today() - timedelta(days=365):  # Não permitir mais de 1 ano no passado
            raise ValueError('Data de vencimento muito antiga')
        return v

    @validator('valor')
    def validar_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return round(v, 2)  # Arredondar para 2 casas decimais

class LancamentoFinanceiroCreate(LancamentoFinanceiroBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    nota_fiscal_id: Optional[str] = None

class LancamentoFinanceiroUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=3, max_length=200)
    valor: Optional[float] = Field(None, gt=0)
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(pendente|pago|atrasado|cancelado)$")
    categoria: Optional[str] = Field(
        None,
        pattern="^(honorarios|impostos|folha_pagamento|aluguel|telefonia|material|servicos|outros)$"
    )
    forma_pagamento: Optional[str] = Field(
        None,
        pattern="^(dinheiro|pix|transferencia|cartao_credito|cartao_debito|boleto)$"
    )
    observacoes: Optional[str] = Field(None, max_length=1000)

    @validator('data_pagamento')
    def validar_data_pagamento(cls, v, values):
        if v and 'data_vencimento' in values and values['data_vencimento']:
            if v < values['data_vencimento']:
                raise ValueError('Data de pagamento não pode ser anterior ao vencimento')
        return v

class LancamentoFinanceiro(LancamentoFinanceiroBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    nota_fiscal_id: Optional[str] = None
    data_pagamento: Optional[date] = Field(None, description="Data de pagamento/recebimento")
    status: str = Field(
        default="pendente",
        pattern="^(pendente|pago|atrasado|cancelado)$",
        description="Status do lançamento"
    )
    data_criacao: datetime
    created_at: datetime
    updated_at: datetime

    # Properties para campos calculados
    @property
    def dias_atraso(self) -> int:
        if self.status == 'atrasado' and self.data_vencimento:
            return max(0, (date.today() - self.data_vencimento).days)
        return 0

    @property
    def esta_vencido(self) -> bool:
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

class LancamentoFinanceiroSummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    descricao: str
    tipo: str
    valor: float
    data_vencimento: date
    status: str
    categoria: str
    dias_atraso: int

    model_config = ConfigDict(from_attributes=True)

# Schemas para Indicadores Financeiros
class IndicadorFinanceiroBase(BaseModel):
    mes_referencia: date = Field(..., description="Mês de referência (primeiro dia do mês)")
    receita_total: float = Field(default=0, ge=0, description="Receita total do mês")
    despesas_total: float = Field(default=0, ge=0, description="Despesas totais do mês")
    despesas_operacionais: float = Field(default=0, ge=0, description="Despesas operacionais")
    despesas_financeiras: float = Field(default=0, ge=0, description="Despesas financeiras")

    @validator('mes_referencia')
    def validar_mes_referencia(cls, v):
        if v.day != 1:
            raise ValueError('mes_referencia deve ser o primeiro dia do mês')
        return v

class IndicadorFinanceiroCreate(IndicadorFinanceiroBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str

class IndicadorFinanceiroUpdate(BaseModel):
    receita_total: Optional[float] = Field(None, ge=0)
    despesas_total: Optional[float] = Field(None, ge=0)
    despesas_operacionais: Optional[float] = Field(None, ge=0)
    despesas_financeiras: Optional[float] = Field(None, ge=0)

class IndicadorFinanceiro(IndicadorFinanceiroBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    created_at: datetime
    updated_at: datetime

    # Properties para campos calculados
    @property
    def lucro_liquido(self) -> float:
        return self.receita_total - self.despesas_total

    @property
    def margem_lucro(self) -> float:
        if self.receita_total > 0:
            return (self.lucro_liquido / self.receita_total) * 100
        return 0.0

    @property
    def inadimplencia(self) -> float:
        # NOTA: Este campo precisa ser calculado baseado nos lançamentos
        return 0.0

    @property
    def fluxo_caixa(self) -> float:
        return self.receita_total - self.despesas_total

    @property
    def situacao_financeira(self) -> str:
        if self.margem_lucro > 20:
            return "excelente"
        elif self.margem_lucro > 10:
            return "boa"
        elif self.margem_lucro > 0:
            return "regular"
        else:
            return "critica"

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class IndicadorFinanceiroSummary(BaseModel):
    mes_referencia: date
    receita_total: float
    lucro_liquido: float
    margem_lucro: float
    situacao: str

    model_config = ConfigDict(from_attributes=True)

# Schemas para Fluxo de Caixa
class FluxoCaixaDia(BaseModel):
    data: date
    receitas: float
    despesas: float
    saldo_dia: float
    saldo_acumulado: float

class FluxoCaixaResponse(BaseModel):
    periodo: Dict[str, date]
    totais: Dict[str, float]
    realizado: Dict[str, float]
    pendente: Dict[str, float]
    fluxo_detalhado: Dict[str, FluxoCaixaDia]
    total_lancamentos: int

class PrevisaoCaixaDia(BaseModel):
    data: date
    receitas_previstas: float
    despesas_previstas: float
    saldo_dia_previsto: float
    saldo_acumulado_previsto: float
    lancamentos: List[LancamentoFinanceiroSummary]

class PrevisaoCaixaResponse(BaseModel):
    periodo: Dict[str, date]
    previsao: Dict[str, PrevisaoCaixaDia]
    totais_previstos: Dict[str, float]
    saldo_final_previsto: float

# Schemas para Dashboard Financeiro
class DashboardFinanceiroResponse(BaseModel):
    periodo: str
    data_inicio: date
    metricas_principales: Dict[str, float]
    receitas_por_categoria: Dict[str, float]
    despesas_por_categoria: Dict[str, float]
    evolucao_mensal: List[IndicadorFinanceiroSummary]
    top_clientes: List[Dict[str, Any]]
    alertas: List[Dict[str, Any]]

class MetricaFinanceira(BaseModel):
    nome: str
    valor: float
    variacao: float
    icone: str
    cor: str

# Schemas para Relatórios
class RelatorioReceitasDespesas(BaseModel):
    periodo: Dict[str, date]
    totais: Dict[str, float]
    receitas_por_categoria: Dict[str, float]
    despesas_por_categoria: Dict[str, float]
    top_lancamentos: List[LancamentoFinanceiroSummary]
    evolucao_mensal: List[Dict[str, Any]]

class RelatorioInadimplencia(BaseModel):
    periodo: Dict[str, date]
    taxa_inadimplencia: float
    valor_total_inadimplente: float
    lancamentos_atrasados: List[LancamentoFinanceiroSummary]
    clientes_inadimplentes: List[Dict[str, Any]]
    evolucao_inadimplencia: List[Dict[str, Any]]

# Schemas para Cálculos Automáticos
class CalculoIndicadoresAuto(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    mes_referencia: date
    lancamentos_receita: List[LancamentoFinanceiroSummary] = Field(default_factory=list)
    lancamentos_despesa: List[LancamentoFinanceiroSummary] = Field(default_factory=list)

class IndicadoresAutoCalculados(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    mes_referencia: date
    receita_total: float
    despesas_total: float
    lucro_liquido: float
    margem_lucro: float
    inadimplencia: float
    fluxo_caixa: float

# Schemas para Filtros e Consultas
class LancamentoFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: Optional[str] = None
    tipo: Optional[str] = Field(None, pattern="^(receita|despesa)$")
    status: Optional[str] = Field(None, pattern="^(pendente|pago|atrasado|cancelado)$")
    categoria: Optional[str] = Field(
        None,
        pattern="^(honorarios|impostos|folha_pagamento|aluguel|telefonia|material|servicos|outros)$"
    )
    data_vencimento_inicio: Optional[date] = None
    data_vencimento_fim: Optional[date] = None
    data_pagamento_inicio: Optional[date] = None
    data_pagamento_fim: Optional[date] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None

class IndicadorFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: Optional[str] = None
    mes_referencia: Optional[date] = None
    ano: Optional[int] = None
    margem_minima: Optional[float] = None
    margem_maxima: Optional[float] = None

# Response Models para Listagens
class LancamentoListResponse(BaseModel):
    items: List[LancamentoFinanceiro]
    total: int
    page: int
    size: int
    pages: int
    totais: Dict[str, float]

class IndicadorListResponse(BaseModel):
    items: List[IndicadorFinanceiro]
    total: int
    page: int
    size: int
    pages: int

# Schemas para Operações Específicas
class PagamentoLancamento(BaseModel):
    data_pagamento: date = Field(..., description="Data do pagamento")
    forma_pagamento: str = Field(
        ...,
        pattern="^(dinheiro|pix|transferencia|cartao_credito|cartao_debito|boleto)$",
        description="Forma de pagamento"
    )
    observacoes: Optional[str] = Field(None, max_length=1000)

class TransferenciaEntreContas(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    lancamento_origem_id: str
    lancamento_destino_id: str
    valor: float = Field(..., gt=0)
    data_transferencia: date
    observacoes: Optional[str] = Field(None, max_length=1000)

# Schemas para Análises
class AnaliseFinanceiraCliente(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    nome_cliente: str
    indicador_ultimo_mes: Optional[IndicadorFinanceiroSummary]
    total_receitas: float
    total_despesas: float
    lancamentos_pendentes: int
    lancamentos_atrasados: int
    situacao: str
    recomendacoes: List[str]

class ComparativoMensal(BaseModel):
    mes_atual: IndicadorFinanceiroSummary
    mes_anterior: Optional[IndicadorFinanceiroSummary]
    variacao_receita: float
    variacao_lucro: float
    variacao_margem: float