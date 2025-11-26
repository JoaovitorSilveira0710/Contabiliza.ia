from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date
from .database import Base

class NotaFiscal(Base):
    __tablename__ = 'notas_fiscais'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey('clientes.id'), nullable=False)
    numero = Column(String(50), nullable=False)
    serie = Column(String(10), default="1")
    chave_acesso = Column(String(44), unique=True)
    tipo = Column(String(10), nullable=False)  # entrada, saida, servico
    modelo = Column(String(10), default="nfe")  # nfe, nfce, nfse
    data_emissao = Column(DateTime, nullable=False)
    data_autorizacao = Column(DateTime)
    valor_total = Column(Float, nullable=False)
    valor_produtos = Column(Float, default=0.0)
    valor_servicos = Column(Float, default=0.0)
    valor_desconto = Column(Float, default=0.0)
    valor_frete = Column(Float, default=0.0)
    valor_seguro = Column(Float, default=0.0)
    valor_outros = Column(Float, default=0.0)
    situacao = Column(String(20), default="autorizada")  # autorizada, cancelada, denegada, rejeitada
    cnpj_emitente = Column(String(20))
    nome_emitente = Column(String(200))
    cnpj_destinatario = Column(String(20))
    nome_destinatario = Column(String(200))
    municipio = Column(String(100))
    uf = Column(String(2))
    xml_path = Column(Text)
    pdf_path = Column(Text)
    observacoes = Column(Text)
    data_importacao = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 🔥 CORREÇÃO CRÍTICA: Usar backref em vez de back_populates
    cliente = relationship("Cliente", backref="notas_fiscais")
    
    # 🔥 CORREÇÃO: Comentar relacionamentos problemáticos
    # lancamentos_financeiros = relationship("LancamentoFinanceiro", back_populates="nota_fiscal")
    
    # Relacionamento interno pode manter
    itens = relationship("ItemNotaFiscal", back_populates="nota_fiscal", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("tipo IN ('entrada', 'saida', 'servico')", name='check_tipo_nota'),
        CheckConstraint("modelo IN ('nfe', 'nfce', 'nfse')", name='check_modelo_nota'),
        CheckConstraint("situacao IN ('autorizada', 'cancelada', 'denegada', 'rejeitada', 'pendente')", name='check_situacao_nota'),
        CheckConstraint("valor_total >= 0", name='check_valor_total_positive'),
        CheckConstraint("valor_total = valor_produtos + valor_servicos - valor_desconto + valor_frete + valor_seguro + valor_outros", name='check_valor_total_calculo'),
        CheckConstraint("length(chave_acesso) = 44 OR chave_acesso IS NULL", name='check_chave_acesso_length'),
    )
    
    @property
    def base_calculo_icms(self):
        return (self.valor_produtos or 0.0) + (self.valor_frete or 0.0) + (self.valor_seguro or 0.0) - (self.valor_desconto or 0.0)
    
    @property
    def e_entrada(self):
        return self.tipo == 'entrada'
    
    @property
    def e_saida(self):
        return self.tipo == 'saida'
    
    @property
    def e_servico(self):
        return self.tipo == 'servico'
    
    @property
    def esta_autorizada(self):
        return self.situacao == 'autorizada'
    
    @property
    def esta_cancelada(self):
        return self.situacao == 'cancelada'
    
    @property
    def dias_desde_emissao(self):
        if not self.data_emissao:
            return None
        hoje = datetime.now()
        return (hoje - self.data_emissao).days
    
    @property
    def mes_emissao(self):
        return self.data_emissao.strftime("%Y-%m") if self.data_emissao else None
    
    def gerar_lancamento_financeiro(self):
        if self.esta_autorizada and self.e_saida:
            return {
                'cliente_id': self.cliente_id,
                'nota_fiscal_id': self.id,
                'tipo': 'receita',
                'descricao': f'NF {self.numero} - {self.nome_destinatario}',
                'valor': self.valor_total,
                'data_vencimento': self.data_emissao.date() if self.data_emissao else None,
                'categoria': 'honorarios' if self.e_servico else 'vendas'
            }
        elif self.esta_autorizada and self.e_entrada:
            return {
                'cliente_id': self.cliente_id,
                'nota_fiscal_id': self.id,
                'tipo': 'despesa',
                'descricao': f'NF Entrada {self.numero} - {self.nome_emitente}',
                'valor': self.valor_total,
                'data_vencimento': self.data_emissao.date() if self.data_emissao else None,
                'categoria': 'compras'
            }
        return None

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


class ItemNotaFiscal(Base):
    __tablename__ = 'itens_nota_fiscal'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nota_fiscal_id = Column(String(36), ForeignKey('notas_fiscais.id'), nullable=False)
    numero_item = Column(Integer, nullable=False)
    codigo_produto = Column(String(50))
    descricao = Column(String(200), nullable=False)
    ncm = Column(String(10))
    cfop = Column(String(10))
    unidade = Column(String(10))
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)
    valor_desconto = Column(Float, default=0.0)
    icms_cst = Column(String(10))
    icms_aliquota = Column(Float, default=0.0)
    icms_valor = Column(Float, default=0.0)
    pis_cst = Column(String(10))
    pis_aliquota = Column(Float, default=0.0)
    pis_valor = Column(Float, default=0.0)
    cofins_cst = Column(String(10))
    cofins_aliquota = Column(Float, default=0.0)
    cofins_valor = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento interno pode manter back_populates
    nota_fiscal = relationship("NotaFiscal", back_populates="itens")
    
    __table_args__ = (
        CheckConstraint("quantidade > 0", name='check_quantidade_positive'),
        CheckConstraint("valor_unitario >= 0", name='check_valor_unitario_positive'),
        CheckConstraint("valor_total = quantidade * valor_unitario - valor_desconto", name='check_valor_total_calculo_item'),
    )
    
    @property
    def valor_liquido(self):
        return (self.quantidade or 0.0) * (self.valor_unitario or 0.0) - (self.valor_desconto or 0.0)
    
    @property
    def valor_impostos(self):
        return (self.icms_valor or 0.0) + (self.pis_valor or 0.0) + (self.cofins_valor or 0.0)
    
    @property
    def aliquota_total_impostos(self):
        vl = self.valor_liquido
        if vl > 0:
            return (self.valor_impostos / vl) * 100
        return 0

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


class EventoNotaFiscal(Base):
    __tablename__ = 'eventos_nota_fiscal'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nota_fiscal_id = Column(String(36), ForeignKey('notas_fiscais.id'), nullable=False)
    tipo_evento = Column(String(50), nullable=False)  # cancelamento, carta_correcao, inutilizacao
    numero_sequencial = Column(Integer, nullable=False)
    data_evento = Column(DateTime, nullable=False)
    protocolo = Column(String(50))
    descricao = Column(Text)
    justificativa = Column(Text)
    xml_evento = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 🔥 CORREÇÃO: Relacionamento simples
    nota_fiscal = relationship("NotaFiscal")
    
    __table_args__ = (
        CheckConstraint("tipo_evento IN ('cancelamento', 'carta_correcao', 'inutilizacao', 'epce')", name='check_tipo_evento'),
    )

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