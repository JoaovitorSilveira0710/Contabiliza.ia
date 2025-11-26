from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date
from .database import Base

class DRE(Base):
    __tablename__ = "dres"
    __table_args__ = (
        CheckConstraint("length(periodo) = 7 AND substr(periodo,5,1) = '-'", name='check_formato_periodo'),
        {'extend_existing': True}
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    periodo = Column(String(7), nullable=False)
    receita_bruta = Column(Float, default=0.0)
    deducoes = Column(Float, default=0.0)
    receita_liquida = Column(Float, default=0.0)
    custos = Column(Float, default=0.0)
    lucro_bruto = Column(Float, default=0.0)
    despesas_operacionais = Column(Float, default=0.0)
    lucro_operacional = Column(Float, default=0.0)
    despesas_nao_operacionais = Column(Float, default=0.0)
    lucro_liquido = Column(Float, default=0.0)
    margem_lucro = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔥 CORREÇÃO: Remover back_populates para evitar conflitos
    cliente = relationship("Cliente", backref="dres")

    def calcular_todos(self):
        self.receita_liquida = (self.receita_bruta or 0.0) - (self.deducoes or 0.0)
        self.lucro_bruto = (self.receita_liquida or 0.0) - (self.custos or 0.0)
        self.lucro_operacional = (self.lucro_bruto or 0.0) - (self.despesas_operacionais or 0.0)
        self.lucro_liquido = (self.lucro_operacional or 0.0) - (self.despesas_nao_operacionais or 0.0)
        self.margem_lucro = ((self.lucro_liquido / self.receita_bruta) * 100) if (self.receita_bruta or 0) > 0 else 0
        return self

class ObrigacaoAcessoria(Base):
    __tablename__ = "obrigacoes_acessorias"
    __table_args__ = (
        CheckConstraint("periodicidade IN ('mensal', 'trimestral', 'anual')", name='check_periodicidade_obrigacao'),
        CheckConstraint("status IN ('pendente', 'entregue', 'atrasado')", name='check_status_obrigacao'),
        {'extend_existing': True}
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    descricao = Column(String(200), nullable=False)
    periodicidade = Column(String(20), nullable=False)
    data_vencimento = Column(Date, nullable=False)
    status = Column(String(20), default="pendente")
    data_entrega = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔥 CORREÇÃO: Remover back_populates para evitar conflitos
    cliente = relationship("Cliente", backref="obrigacoes_acessorias")

    @property
    def dias_para_vencer(self):
        if self.data_vencimento:
            hoje = date.today()
            return (self.data_vencimento - hoje).days
        return None

    @property
    def esta_atrasada(self):
        if self.data_vencimento:
            return date.today() > self.data_vencimento and self.status != "entregue"
        return False

    def atualizar_status_automatico(self):
        if self.data_entrega:
            self.status = "entregue"
        elif self.esta_atrasada:
            self.status = "atrasado"
        else:
            self.status = "pendente"
        return self

# Utilitário local simples
class ModelMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        import json
        from datetime import date, datetime as dt
        import uuid as _uuid
        
        def serializer(o):
            if isinstance(o, (dt, date)):
                return o.isoformat()
            if isinstance(o, _uuid.UUID):
                return str(o)
            return str(o)
        
        data = self.to_dict()
        return json.dumps(data, default=serializer, ensure_ascii=False)

# Aplicar mixin apenas aos models DEFINIDOS NESTE ARQUIVO
for model_class in [DRE, ObrigacaoAcessoria]:
    model_class.to_dict = ModelMixin.to_dict
    model_class.to_json = ModelMixin.to_json