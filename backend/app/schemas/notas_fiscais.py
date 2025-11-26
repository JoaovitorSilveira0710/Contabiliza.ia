from pydantic import BaseModel, validator, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import re

class NotaFiscalBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=50, description="Número da nota fiscal")
    serie: Optional[str] = Field("1", max_length=10, description="Série da nota fiscal")
    chave_acesso: Optional[str] = Field(None, min_length=44, max_length=44, description="Chave de acesso (44 caracteres)")
    tipo: str = Field(
        ..., 
        pattern="^(entrada|saida|servico)$",
        description="Tipo da nota: entrada, saida ou servico"
    )
    modelo: str = Field(
        default="nfe",
        pattern="^(nfe|nfce|nfse)$",
        description="Modelo da nota: nfe, nfce ou nfse"
    )
    data_emissao: datetime = Field(..., description="Data e hora de emissão")
    data_autorizacao: Optional[datetime] = Field(None, description="Data e hora de autorização")
    valor_total: float = Field(..., gt=0, description="Valor total da nota")
    valor_produtos: float = Field(default=0, ge=0, description="Valor total dos produtos")
    valor_servicos: float = Field(default=0, ge=0, description="Valor total dos serviços")
    valor_desconto: float = Field(default=0, ge=0, description="Valor do desconto")
    valor_frete: float = Field(default=0, ge=0, description="Valor do frete")
    valor_seguro: float = Field(default=0, ge=0, description="Valor do seguro")
    valor_outros: float = Field(default=0, ge=0, description="Outros valores")
    cnpj_emitente: Optional[str] = Field(None, max_length=18, description="CNPJ do emitente (com ou sem formatação)")
    nome_emitente: Optional[str] = Field(None, max_length=200, description="Nome do emitente")
    cnpj_destinatario: Optional[str] = Field(None, max_length=18, description="CNPJ do destinatário (com ou sem formatação)")
    nome_destinatario: Optional[str] = Field(None, max_length=200, description="Nome do destinatário")
    municipio: Optional[str] = Field(None, max_length=100, description="Município de emissão")
    uf: Optional[str] = Field(None, min_length=2, max_length=2, description="UF de emissão")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")

    @validator('chave_acesso')
    def validar_chave_acesso(cls, v):
        if v and len(v) != 44:
            raise ValueError('Chave de acesso deve ter 44 caracteres')
        if v and not v.isdigit():
            raise ValueError('Chave de acesso deve conter apenas dígitos')
        return v

    @validator('cnpj_emitente', 'cnpj_destinatario')
    def limpar_cnpj(cls, v):
        """Remove formatação do CNPJ mantendo apenas dígitos"""
        if v:
            v = re.sub(r'[^\d]', '', v)  # Remove tudo exceto dígitos
            if len(v) not in [11, 14]:  # Aceita CPF (11) ou CNPJ (14)
                raise ValueError('CNPJ/CPF inválido')
        return v

    @validator('uf')
    def validar_uf(cls, v):
        ufs_validas = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        if v and v.upper() not in ufs_validas:
            raise ValueError('UF inválida')
        return v.upper() if v else v

    @validator('valor_total')
    def validar_valor_total(cls, v, values):
        """Validação flexível do valor total - apenas arredonda"""
        return round(v, 2)

class NotaFiscalCreate(NotaFiscalBase):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: str
    
    @validator('data_autorizacao')
    def validar_data_autorizacao(cls, v, values):
        if v and 'data_emissao' in values and values['data_emissao']:
            # Permitir tolerância de 1 segundo para casos de emissão e autorização quase simultâneas
            diferenca = (v - values['data_emissao']).total_seconds()
            if diferenca < -1:  # Só falha se for mais de 1 segundo antes
                raise ValueError('Data de autorização não pode ser anterior à emissão')
        return v

class NotaFiscalUpdate(BaseModel):
    numero: Optional[str] = Field(None, min_length=1, max_length=50)
    serie: Optional[str] = Field(None, max_length=10)
    situacao: Optional[str] = Field(
        None,
        pattern="^(autorizada|cancelada|denegada|rejeitada|pendente)$"
    )
    data_autorizacao: Optional[datetime] = None
    valor_total: Optional[float] = Field(None, gt=0)
    valor_produtos: Optional[float] = Field(None, ge=0)
    valor_servicos: Optional[float] = Field(None, ge=0)
    valor_desconto: Optional[float] = Field(None, ge=0)
    observacoes: Optional[str] = Field(None, max_length=1000)

class NotaFiscal(NotaFiscalBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    cliente_id: str
    situacao: str = Field(
        default="autorizada",
        pattern="^(autorizada|cancelada|denegada|rejeitada|pendente)$",
        description="Situação da nota fiscal"
    )
    xml_path: Optional[str] = Field(None, description="Caminho do arquivo XML")
    pdf_path: Optional[str] = Field(None, description="Caminho do arquivo PDF")
    data_importacao: datetime
    created_at: datetime
    updated_at: datetime

    # Properties para campos calculados
    @property
    def base_calculo_icms(self) -> float:
        return (self.valor_produtos + self.valor_frete + self.valor_seguro - 
                self.valor_desconto)

    @property
    def e_entrada(self) -> bool:
        return self.tipo == 'entrada'

    @property
    def e_saida(self) -> bool:
        return self.tipo == 'saida'

    @property
    def e_servico(self) -> bool:
        return self.tipo == 'servico'

    @property
    def esta_autorizada(self) -> bool:
        return self.situacao == 'autorizada'

    @property
    def esta_cancelada(self) -> bool:
        return self.situacao == 'cancelada'

    @property
    def dias_desde_emissao(self) -> int:
        return (datetime.now() - self.data_emissao).days

    @property
    def mes_emissao(self) -> str:
        return self.data_emissao.strftime("%Y-%m")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class NotaFiscalSummary(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    numero: str
    tipo: str
    modelo: str
    data_emissao: datetime
    valor_total: float
    situacao: str
    cnpj_emitente: Optional[str]
    cnpj_destinatario: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# Schemas para Itens da Nota Fiscal
class ItemNotaFiscalBase(BaseModel):
    numero_item: int = Field(..., ge=1, description="Número sequencial do item")
    codigo_produto: Optional[str] = Field(None, max_length=50, description="Código do produto/serviço")
    descricao: str = Field(..., min_length=1, max_length=200, description="Descrição do item")
    ncm: Optional[str] = Field(None, min_length=8, max_length=8, description="NCM do produto")
    cfop: Optional[str] = Field(None, min_length=4, max_length=4, description="CFOP")
    unidade: Optional[str] = Field(None, max_length=10, description="Unidade de medida")
    quantidade: float = Field(..., gt=0, description="Quantidade")
    valor_unitario: float = Field(..., gt=0, description="Valor unitário")
    valor_desconto: float = Field(default=0, ge=0, description="Valor do desconto no item")
    icms_cst: Optional[str] = Field(None, max_length=10, description="CST do ICMS")
    icms_aliquota: float = Field(default=0, ge=0, le=100, description="Alíquota do ICMS")
    pis_cst: Optional[str] = Field(None, max_length=10, description="CST do PIS")
    pis_aliquota: float = Field(default=0, ge=0, le=100, description="Alíquota do PIS")
    cofins_cst: Optional[str] = Field(None, max_length=10, description="CST do COFINS")
    cofins_aliquota: float = Field(default=0, ge=0, le=100, description="Alíquota do COFINS")

    @validator('ncm')
    def validar_ncm(cls, v):
        if v and (len(v) != 8 or not v.isdigit()):
            raise ValueError('NCM deve ter 8 dígitos')
        return v

    @validator('cfop')
    def validar_cfop(cls, v):
        if v and (len(v) != 4 or not v.isdigit()):
            raise ValueError('CFOP deve ter 4 dígitos')
        return v

class ItemNotaFiscalCreate(ItemNotaFiscalBase):
    # 🔥 CORREÇÃO: UUID como string
    nota_fiscal_id: str

class ItemNotaFiscal(ItemNotaFiscalBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    nota_fiscal_id: str
    created_at: datetime

    # Properties para campos calculados
    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario - self.valor_desconto, 2)

    @property
    def icms_valor(self) -> float:
        valor_liquido = self.quantidade * self.valor_unitario - self.valor_desconto
        return round(valor_liquido * (self.icms_aliquota / 100), 2)

    @property
    def pis_valor(self) -> float:
        valor_liquido = self.quantidade * self.valor_unitario - self.valor_desconto
        return round(valor_liquido * (self.pis_aliquota / 100), 2)

    @property
    def cofins_valor(self) -> float:
        valor_liquido = self.quantidade * self.valor_unitario - self.valor_desconto
        return round(valor_liquido * (self.cofins_aliquota / 100), 2)

    @property
    def valor_liquido(self) -> float:
        return self.quantidade * self.valor_unitario - self.valor_desconto

    @property
    def valor_impostos(self) -> float:
        return (self.icms_valor or 0) + (self.pis_valor or 0) + (self.cofins_valor or 0)

    @property
    def aliquota_total_impostos(self) -> float:
        if self.valor_liquido > 0:
            return (self.valor_impostos / self.valor_liquido) * 100
        return 0

    model_config = ConfigDict(from_attributes=True)

# Schemas para Eventos da Nota Fiscal
class EventoNotaFiscalBase(BaseModel):
    tipo_evento: str = Field(
        ...,
        pattern="^(cancelamento|carta_correcao|inutilizacao|epce)$",
        description="Tipo do evento"
    )
    numero_sequencial: int = Field(..., ge=1, description="Número sequencial do evento")
    data_evento: datetime = Field(..., description="Data e hora do evento")
    protocolo: Optional[str] = Field(None, max_length=50, description="Número do protocolo")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do evento")
    justificativa: Optional[str] = Field(None, max_length=1000, description="Justificativa")

class EventoNotaFiscalCreate(EventoNotaFiscalBase):
    # 🔥 CORREÇÃO: UUID como string
    nota_fiscal_id: str

class EventoNotaFiscal(EventoNotaFiscalBase):
    # 🔥 CORREÇÃO: UUID como string
    id: str
    nota_fiscal_id: str
    xml_evento: Optional[str] = Field(None, description="Conteúdo do XML do evento")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schemas para Busca e Importação
class BuscaNotasFiscais(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=14, description="CNPJ para busca")
    data_inicio: date = Field(..., description="Data inicial do período")
    data_fim: date = Field(..., description="Data final do período")
    tipo: str = Field(
        default="todas",
        pattern="^(entrada|saida|todas)$",
        description="Tipo de notas a buscar"
    )

    @validator('data_fim')
    def validar_periodo(cls, v, values):
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError('Data final não pode ser anterior à data inicial')
        if (v - values['data_inicio']).days > 365:
            raise ValueError('Período de busca não pode ser maior que 1 ano')
        return v

class ImportacaoNotasResponse(BaseModel):
    message: str
    notas_importadas: int
    notas_com_erro: int
    total_arquivos: int
    cliente: Optional[str] = None
    cnpj: Optional[str] = None
    periodo: Optional[Dict[str, date]] = None
    tipo: Optional[str] = None
    timestamp: datetime

# Schemas para Dashboard e Relatórios
class DashboardNotasFiscaisResponse(BaseModel):
    periodo: str
    data_inicio: date
    metricas_principais: Dict[str, Any]
    distribuicao: Dict[str, Dict[str, int]]
    top_clientes: List[Dict[str, Any]]
    evolucao_mensal: List[Dict[str, Any]]

class RelatorioConsolidadoResponse(BaseModel):
    periodo: Dict[str, date]
    totais: Dict[str, float]
    distribuicao: Dict[str, Dict[str, int]]
    metricas: Dict[str, float]
    top_notas: List[NotaFiscalSummary]

class EstatisticasMensaisResponse(BaseModel):
    ano: int
    estatisticas: Dict[str, Dict[str, Any]]
    total_ano: Dict[str, Any]

# Schemas para Filtros
class NotaFiscalFilters(BaseModel):
    # 🔥 CORREÇÃO: UUID como string
    cliente_id: Optional[str] = None
    tipo: Optional[str] = Field(None, pattern="^(entrada|saida|servico)$")
    modelo: Optional[str] = Field(None, pattern="^(nfe|nfce|nfse)$")
    situacao: Optional[str] = Field(None, pattern="^(autorizada|cancelada|denegada|rejeitada|pendente)$")
    data_emissao_inicio: Optional[date] = None
    data_emissao_fim: Optional[date] = None
    data_autorizacao_inicio: Optional[date] = None
    data_autorizacao_fim: Optional[date] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    cnpj_emitente: Optional[str] = None
    cnpj_destinatario: Optional[str] = None

# Response Models
class NotaFiscalListResponse(BaseModel):
    items: List[NotaFiscal]
    total: int
    page: int
    size: int
    pages: int
    totais: Dict[str, float]

class NotaFiscalComItens(NotaFiscal):
    itens: List[ItemNotaFiscal] = []
    eventos: List[EventoNotaFiscal] = []

# Schemas para Operações
class CancelamentoNotaFiscal(BaseModel):
    justificativa: str = Field(..., min_length=15, max_length=255, description="Justificativa do cancelamento")
    protocolo: Optional[str] = Field(None, max_length=50, description="Protocolo de autorização")

class AutorizacaoNotaFiscal(BaseModel):
    protocolo: str = Field(..., max_length=50, description="Protocolo de autorização")
    data_autorizacao: Optional[datetime] = None