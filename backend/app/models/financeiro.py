from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date
from .database import Base

class LancamentoFinanceiro(Base):
    __tablename__ = 'lancamentos_financeiros'
    __table_args__ = (
        CheckConstraint("tipo IN ('receita', 'despesa')", name='check_tipo_lancamento'),
        CheckConstraint("status IN ('pendente', 'pago', 'atrasado', 'cancelado')", name='check_status_lancamento'),
        CheckConstraint("valor > 0", name='check_valor_positivo'),
        CheckConstraint(
            "categoria IN ('honorarios', 'impostos', 'folha_pagamento', 'aluguel', 'telefonia', 'material', 'servicos', 'outros')",
            name='check_categoria_lancamento'
        ),
        CheckConstraint(
            "forma_pagamento IN ('dinheiro', 'pix', 'transferencia', 'cartao_credito', 'cartao_debito', 'boleto')",
            name='check_forma_pagamento'
        ),
        {'extend_existing': True}
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    
    # 🔥 PROBLEMA 1: 'notas_fiscais' table não existe - REMOVER
    # nota_fiscal_id = Column(String(36), ForeignKey('notas_fiscais.id'), nullable=True)
    
    tipo = Column(String(20), nullable=False)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    status = Column(String(20), default="pendente")
    categoria = Column(String(50), nullable=True)
    forma_pagamento = Column(String(30), nullable=True)
    observacoes = Column(Text, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 🔥 CORREÇÃO: Remover relacionamento com NotaFiscal que não existe
    # Apenas relacionamento básico com Cliente
    cliente = relationship("Cliente", backref="lancamentos_financeiros")
    
    @property
    def dias_atraso(self):
        """Calcula dias de atraso para lançamentos vencidos"""
        if self.status == 'atrasado' and self.data_vencimento:
            hoje = datetime.now().date()
            return (hoje - self.data_vencimento).days
        return 0
    
    @property
    def esta_vencido(self):
        """Verifica se o lançamento está vencido"""
        if self.status == 'pendente' and self.data_vencimento:
            hoje = datetime.now().date()
            return hoje > self.data_vencimento
        return False
    
    def atualizar_status_automatico(self):
        """Atualiza o status automaticamente baseado nas datas"""
        if self.data_pagamento:
            self.status = 'pago'
        elif self.esta_vencido:
            self.status = 'atrasado'
        else:
            self.status = 'pendente'
    
    def calcular_juros_multa(self, taxa_juros=0.01, taxa_multa=0.02):
        """Calcula juros e multa para lançamentos atrasados"""
        if self.status == 'atrasado' and self.dias_atraso > 0:
            juros = (self.valor or 0.0) * taxa_juros * self.dias_atraso
            multa = (self.valor or 0.0) * taxa_multa
            return {
                'juros': juros,
                'multa': multa,
                'total': (self.valor or 0.0) + juros + multa
            }
        return {'juros': 0, 'multa': 0, 'total': (self.valor or 0.0)}

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


class IndicadorFinanceiro(Base):
    __tablename__ = 'indicadores_financeiros'
    __table_args__ = (
        CheckConstraint("receita_total >= 0", name='check_receita_total_positive'),
        CheckConstraint("despesas_total >= 0", name='check_despesas_total_positive'),
        CheckConstraint("margem_lucro BETWEEN -100 AND 100", name='check_margem_lucro_range'),
        CheckConstraint("inadimplencia BETWEEN 0 AND 100", name='check_inadimplencia_range'),
        CheckConstraint("strftime('%d', mes_referencia) = '01'", name='check_mes_referencia_primeiro_dia'),
        {'extend_existing': True}
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    mes_referencia = Column(Date, nullable=False)
    receita_total = Column(Float, default=0.0)
    despesas_total = Column(Float, default=0.0)
    lucro_liquido = Column(Float, default=0.0)
    margem_lucro = Column(Float, default=0.0)
    inadimplencia = Column(Float, default=0.0)
    fluxo_caixa = Column(Float, default=0.0)
    despesas_operacionais = Column(Float, default=0.0)
    despesas_financeiras = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 🔥 CORREÇÃO: Relacionamento simples
    cliente = relationship("Cliente", backref="indicadores_financeiros")
    
    def calcular_lucro_liquido(self):
        """Calcula o lucro líquido automaticamente"""
        self.lucro_liquido = (self.receita_total or 0.0) - (self.despesas_total or 0.0)
        return self.lucro_liquido
    
    def calcular_margem_lucro(self):
        """Calcula a margem de lucro automaticamente"""
        if (self.receita_total or 0.0) > 0:
            self.margem_lucro = (self.lucro_liquido / self.receita_total) * 100
        else:
            self.margem_lucro = 0
        return self.margem_lucro
    
    def calcular_fluxo_caixa(self):
        """Calcula o fluxo de caixa"""
        self.fluxo_caixa = (self.receita_total or 0.0) - (self.despesas_total or 0.0)
        return self.fluxo_caixa
    
    def calcular_todos(self):
        """Calcula todos os indicadores automaticamente"""
        self.calcular_lucro_liquido()
        self.calcular_margem_lucro()
        self.calcular_fluxo_caixa()
    
    @property
    def situacao_financeira(self):
        """Retorna a situação financeira baseada nos indicadores"""
        if self.margem_lucro > 20:
            return "excelente"
        elif self.margem_lucro > 10:
            return "boa"
        elif self.margem_lucro > 0:
            return "regular"
        else:
            return "critica"
    
    @property
    def trimestre(self):
        """Retorna o trimestre de referência"""
        return (self.mes_referencia.month - 1) // 3 + 1

    # 🔥 PROBLEMA 2: Remover métodos que dependem de relacionamentos não definidos
    # Esses métodos tentam acessar self.lancamentos que não existe no relacionamento
    
    def calcular_receita_mensal(self, db_session, mes=None, ano=None):
        """Calcula a receita total do cliente em um período (versão corrigida)"""
        from . import LancamentoFinanceiro  # Import local para evitar circular
        
        query = db_session.query(LancamentoFinanceiro).filter(
            LancamentoFinanceiro.cliente_id == self.cliente_id,
            LancamentoFinanceiro.tipo == 'receita',
            LancamentoFinanceiro.status == 'pago'
        )
        
        if mes and ano:
            query = query.filter(
                LancamentoFinanceiro.data_pagamento.isnot(None),
                db_session.extract('month', LancamentoFinanceiro.data_pagamento) == mes,
                db_session.extract('year', LancamentoFinanceiro.data_pagamento) == ano
            )
        
        lancamentos = query.all()
        return sum((l.valor or 0.0) for l in lancamentos)
    
    def calcular_despesas_mensal(self, db_session, mes=None, ano=None):
        """Calcula as despesas totais do cliente em um período (versão corrigida)"""
        from . import LancamentoFinanceiro  # Import local para evitar circular
        
        query = db_session.query(LancamentoFinanceiro).filter(
            LancamentoFinanceiro.cliente_id == self.cliente_id,
            LancamentoFinanceiro.tipo == 'despesa',
            LancamentoFinanceiro.status == 'pago'
        )
        
        if mes and ano:
            query = query.filter(
                LancamentoFinanceiro.data_pagamento.isnot(None),
                db_session.extract('month', LancamentoFinanceiro.data_pagamento) == mes,
                db_session.extract('year', LancamentoFinanceiro.data_pagamento) == ano
            )
        
        lancamentos = query.all()
        return sum((l.valor or 0.0) for l in lancamentos)

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
for model_class in [LancamentoFinanceiro, IndicadorFinanceiro]:
    model_class.to_dict = ModelMixin.to_dict
    model_class.to_json = ModelMixin.to_json