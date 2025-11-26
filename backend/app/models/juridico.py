from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date
from .database import Base

class Processo(Base):
    __tablename__ = 'processos'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    numero_processo = Column(String(100), unique=True, nullable=False)
    vara = Column(String(100))
    assunto = Column(String(200), nullable=False)
    data_distribuicao = Column(Date)
    status = Column(String(50), default="ativo")
    valor_causa = Column(Float, default=0.0)
    honorarios = Column(Float, default=0.0)
    honorarios_contratuais = Column(Float, default=0.0)
    tipo_acao = Column(String(100))
    parte_contraria = Column(String(200))
    advogado_responsavel = Column(String(100))
    ultima_movimentacao = Column(Text)
    data_ultima_movimentacao = Column(Date)
    data_prazo = Column(Date)
    observacoes = Column(Text)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos corrigidos
    cliente = relationship("Cliente", backref="processos")
    andamentos = relationship("AndamentoProcessual", back_populates="processo", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('ativo', 'encerrado', 'arquivado', 'suspenso')", name='check_status_processo'),
        CheckConstraint("valor_causa >= 0", name='check_valor_causa_positive'),
        CheckConstraint("honorarios >= 0", name='check_honorarios_positive'),
        CheckConstraint("honorarios_contratuais >= 0", name='check_honorarios_contratuais_positive'),
    )

    @property
    def tempo_tramitacao(self):
        if self.data_distribuicao:
            hoje = datetime.now().date()
            return (hoje - self.data_distribuicao).days
        return 0

    @property
    def dias_para_prazo(self):
        if self.data_prazo:
            hoje = datetime.now().date()
            return (self.data_prazo - hoje).days
        return None

    @property
    def prazo_proximo(self):
        dias = self.dias_para_prazo
        return dias is not None and 0 <= dias <= 7

    @property
    def prazo_vencido(self):
        dias = self.dias_para_prazo
        return dias is not None and dias < 0

    def atualizar_ultima_movimentacao(self, descricao, tipo=None):
        self.ultima_movimentacao = descricao
        self.data_ultima_movimentacao = datetime.now().date()

        andamento = AndamentoProcessual(
            processo_id=self.id,
            descricao=descricao,
            tipo=tipo or "outros"
        )
        self.andamentos.append(andamento)

    @property
    def andamentos_recentes(self):
        return sorted(self.andamentos, key=lambda x: x.data_andamento or datetime.min, reverse=True)[:10]

    @property
    def honorarios_devidos(self):
        return max(0, (self.honorarios_contratuais or 0.0) - (self.honorarios or 0.0))


class AndamentoProcessual(Base):
    __tablename__ = 'andamentos_processuais'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processo_id = Column(String(36), ForeignKey('processos.id'), nullable=False)
    data_andamento = Column(DateTime, default=datetime.utcnow)
    descricao = Column(Text, nullable=False)
    tipo = Column(String(50))
    resultado = Column(String(100))
    observacoes = Column(Text)
    usuario_responsavel = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    processo = relationship("Processo", back_populates="andamentos")

    __table_args__ = (
        CheckConstraint("tipo IN ('sentenca', 'despacho', 'audiencia', 'peticao', 'citacao', 'intimacao', 'outros')", name='check_tipo_andamento'),
        CheckConstraint("resultado IN ('favoravel', 'desfavoravel', 'neutro', 'parcial')", name='check_resultado_andamento'),
    )

    @property
    def e_favoravel(self):
        return self.resultado == 'favoravel'

    @property
    def e_desfavoravel(self):
        return self.resultado == 'desfavoravel'

    @property
    def dias_desde_andamento(self):
        if not self.data_andamento:
            return None
        hoje = datetime.now()
        return (hoje - self.data_andamento).days


class Audiencia(Base):
    __tablename__ = 'audiencias'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processo_id = Column(String(36), ForeignKey('processos.id'), nullable=False)
    data_audiencia = Column(DateTime, nullable=False)
    tipo = Column(String(50))
    local = Column(String(200))
    resultado = Column(Text)
    comparecimento = Column(Boolean)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    processo = relationship("Processo")

    __table_args__ = (
        CheckConstraint("tipo IN ('instrucao', 'conciliacao', 'julgamento', 'diligencia')", name='check_tipo_audiencia'),
    )

    @property
    def dias_para_audiencia(self):
        hoje = datetime.now()
        return (self.data_audiencia - hoje).days if self.data_audiencia and self.data_audiencia > hoje else 0

    @property
    def audiencia_proxima(self):
        dias = self.dias_para_audiencia
        return 0 <= dias <= 7


# Métodos utilitários simplificados
def add_model_mixin(model_class):
    """Adiciona métodos to_dict e to_json à classe do modelo"""
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
    
    model_class.to_dict = to_dict
    model_class.to_json = to_json


# Aplicar mixin aos modelos
for model_class in [Processo, AndamentoProcessual, Audiencia]:
    add_model_mixin(model_class)