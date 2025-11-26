from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from .database import Base

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome_razao_social = Column(String(200), nullable=False)
    cnpj_cpf = Column(String(20), unique=True, nullable=False)
    email = Column(String(100))
    telefone = Column(String(20))
    
    # Endereço detalhado
    cep = Column(String(10))
    logradouro = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    endereco = Column(Text)  # Mantido para compatibilidade
    
    tipo_pessoa = Column(String(1), nullable=False)
    inscricao_estadual = Column(String(20))
    inscricao_municipal = Column(String(20))
    regime_tributario = Column(String(50))
    data_abertura = Column(Date)
    atividade_principal = Column(String(200))
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("tipo_pessoa IN ('F', 'J')", name='check_tipo_pessoa'),
        CheckConstraint("regime_tributario IN ('Simples Nacional', 'Lucro Presumido', 'Lucro Real', 'MEI')", name='check_regime_tributario'),
        {'extend_existing': True}
    )

    # 🔥 CORREÇÃO: Remover relacionamentos problemáticos ou usar LAZY loading
    # Manter apenas relacionamentos com classes definidas NESTE arquivo
    contratos = relationship("Contrato", back_populates="cliente", cascade="all, delete-orphan")
    
    # 🔥 CORREÇÃO: Comentar relacionamentos com classes de outros arquivos
    # Ou remover completamente se não forem essenciais
    # notas_fiscais = relationship("NotaFiscal", cascade="all, delete-orphan")
    # processos = relationship("Processo", cascade="all, delete-orphan")
    # obrigacoes = relationship("ObrigacaoAcessoria", cascade="all, delete-orphan")
    # lancamentos = relationship("LancamentoFinanceiro", cascade="all, delete-orphan")
    # dres = relationship("DRE", cascade="all, delete-orphan")
    # indicadores_financeiros = relationship("IndicadorFinanceiro", cascade="all, delete-orphan")

class Contrato(Base):
    __tablename__ = 'contratos'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    tipo_servico = Column(String(50), nullable=False)
    valor_mensal = Column(Float, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_termino = Column(Date)
    dia_vencimento = Column(Integer, nullable=False)
    status = Column(String(20), default="ativo")
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('ativo', 'inativo', 'suspenso', 'cancelado')", name='check_status_contrato'),
        CheckConstraint("dia_vencimento BETWEEN 1 AND 31", name='check_dia_vencimento'),
        CheckConstraint("tipo_servico IN ('contabil', 'juridico', 'ambos')", name='check_tipo_servico'),
    )

    cliente = relationship("Cliente", back_populates="contratos")
    servicos = relationship("ServicoContratado", back_populates="contrato", cascade="all, delete-orphan")

class ServicoContratado(Base):
    __tablename__ = 'servicos_contratados'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contrato_id = Column(String(36), ForeignKey('contratos.id'), nullable=False)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    periodicidade = Column(String(20), default="mensal")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("periodicidade IN ('mensal', 'trimestral', 'anual', 'unico')", name='check_periodicidade'),
    )

    contrato = relationship("Contrato", back_populates="servicos")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(20), default="contador")
    ativo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("tipo IN ('admin', 'contador', 'assistente')", name='check_tipo_usuario'),
    )

    metricas = relationship("DashboardMetrica", back_populates="usuario", cascade="all, delete-orphan")
    auditorias = relationship("Auditoria", back_populates="usuario", cascade="all, delete-orphan")

class DashboardMetrica(Base):
    __tablename__ = 'dashboard_metricas'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey('usuarios.id'), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(30), nullable=False)
    periodo = Column(String(20), default="mensal")
    valor = Column(Float, nullable=False)
    data_referencia = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("tipo IN ('receita_total', 'despesa_total', 'lucro_liquido', 'clientes_ativos', 'processos_ativos', 'obrigacoes_pendentes')", name='check_tipo_metrica'),
        CheckConstraint("periodo IN ('diario', 'semanal', 'mensal', 'anual')", name='check_periodo_metrica'),
    )

    usuario = relationship("Usuario", back_populates="metricas")

class Auditoria(Base):
    __tablename__ = 'auditoria'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey('usuarios.id'), nullable=False)
    acao = Column(String(50), nullable=False)
    tabela_afetada = Column(String(50), nullable=False)
    registro_id = Column(String(36), nullable=False)
    dados_anteriores = Column(Text)
    dados_novos = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("acao IN ('criar', 'atualizar', 'deletar', 'login', 'logout', 'exportar')", name='check_acao_auditoria'),
    )

    usuario = relationship("Usuario", back_populates="auditorias")

# Métodos utilitários
class ModelMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def to_json(self):
        import json
        from datetime import date, datetime
        import uuid as _uuid
        
        def json_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, _uuid.UUID):
                return str(obj)
            return str(obj)
        
        data = self.to_dict()
        return json.dumps(data, default=json_serializer, ensure_ascii=False)

# Aplicar mixin apenas aos models definidos neste arquivo
for model_class in [Cliente, Contrato, ServicoContratado, Usuario, DashboardMetrica, Auditoria]:
    model_class.to_dict = ModelMixin.to_dict
    model_class.to_json = ModelMixin.to_json