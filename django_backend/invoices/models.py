from django.db import models
from django.conf import settings
from clients.models import Client
import uuid


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('pending', 'Pendente'),
        ('authorized', 'Autorizada'),
        ('cancelled', 'Cancelada'),
        ('denied', 'Denegada'),
    ]
    
    INVOICE_TYPE_CHOICES = [
        ('nfe', 'NF-e - Nota Fiscal Eletrônica'),
        ('nfse', 'NFS-e - Nota Fiscal de Serviço'),
        ('nfce', 'NFC-e - Nota Fiscal ao Consumidor'),
    ]
    
    OPERATION_NATURE_CHOICES = [
        ('venda_producao', 'Venda de produção do estabelecimento'),
        ('venda_mercadoria', 'Venda de mercadoria adquirida/recebida de terceiros'),
        ('venda_soja', 'Venda de Soja'),
        ('prestacao_servico', 'Prestação de serviço'),
        ('devolucao', 'Devolução de mercadoria'),
        ('transferencia', 'Transferência'),
        ('remessa', 'Remessa'),
        ('outras', 'Outras'),
    ]
    
    OPERATION_TYPE_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    FREIGHT_MODE_CHOICES = [
        ('0', '0-Emitente'),
        ('1', '1-Destinatário'),
        ('2', '2-Terceiros'),
        ('3', '3-Próprio remetente'),
        ('4', '4-Próprio destinatário'),
        ('9', '9-Sem frete'),
    ]
    
    PAYMENT_INDICATOR_CHOICES = [
        ('0', '0-À vista'),
        ('1', '1-À prazo'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('01', '01-Dinheiro'),
        ('02', '02-Cheque'),
        ('03', '03-Cartão Crédito'),
        ('04', '04-Cartão Débito'),
        ('05', '05-Crédito Loja'),
        ('10', '10-Vale Alimentação'),
        ('11', '11-Vale Refeição'),
        ('12', '12-Vale Presente'),
        ('13', '13-Vale Combustível'),
        ('14', '14-Duplicata Mercantil'),
        ('15', '15-Boleto Bancário'),
        ('90', '90-Sem pagamento'),
        ('99', '99-Outros'),
    ]
    
    FINAL_CONSUMER_CHOICES = [
        ('0', '0-Normal'),
        ('1', '1-Consumidor Final'),
    ]
    
    PRESENCE_INDICATOR_CHOICES = [
        ('0', '0-Não se aplica'),
        ('1', '1-Presencial'),
        ('2', '2-Internet'),
        ('3', '3-Teleatendimento'),
        ('4', '4-Entrega domicílio'),
        ('9', '9-Outros'),
    ]
    
    DESTINATION_INDICATOR_CHOICES = [
        ('1', '1-Interna'),
        ('2', '2-Interestadual'),
        ('3', '3-Exterior'),
    ]
    
    IE_INDICATOR_CHOICES = [
        ('1', '1-Contribuinte ICMS'),
        ('2', '2-Isento'),
        ('9', '9-Não Contribuinte'),
    ]
    
    TAX_REGIME_CHOICES = [
        ('1', '1-Simples Nacional'),
        ('2', '2-Simples Nacional - excesso'),
        ('3', '3-Regime Normal'),
    ]
    
    ENVIRONMENT_CHOICES = [
        ('1', '1-Produção'),
        ('2', '2-Homologação'),
    ]

    # Identification
    number = models.CharField(max_length=20, unique=True, verbose_name='Número')
    series = models.CharField(max_length=10, default='1', verbose_name='Série')
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE_CHOICES, default='nfe')
    model_code = models.CharField(max_length=2, default='55', verbose_name='Código do Modelo')  # 55=NFe, 65=NFCe
    access_key = models.CharField(max_length=44, blank=True, null=True, unique=True, verbose_name='Chave de Acesso')
    
    # Operation Details
    operation_nature = models.CharField(max_length=60, choices=OPERATION_NATURE_CHOICES, default='venda_producao', verbose_name='Natureza da Operação')
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPE_CHOICES, default='saida', verbose_name='Tipo de Operação')
    cfop = models.CharField(max_length=4, default='5101', verbose_name='CFOP')  # Fiscal Operation Code
    
    # Parties - Issuer (Emitente)
    issuer_name = models.CharField(max_length=200, verbose_name='Nome/Razão Social do Emitente')
    issuer_tax_id = models.CharField(max_length=20, verbose_name='CNPJ Emitente')
    issuer_fantasy_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nome Fantasia Emitente')
    issuer_state_registration = models.CharField(max_length=20, blank=True, null=True, verbose_name='Inscrição Estadual Emitente')
    issuer_address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Endereço Emitente')
    issuer_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número Emitente')
    issuer_district = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bairro Emitente')
    issuer_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Município Emitente')
    issuer_city_code = models.CharField(max_length=7, blank=True, null=True, verbose_name='Código Município Emitente')  # IBGE Code
    issuer_state = models.CharField(max_length=2, blank=True, null=True, verbose_name='UF Emitente')
    issuer_zip_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='CEP Emitente')
    issuer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone Emitente')
    
    # Parties - Receiver (Destinatário)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices', verbose_name='Cliente/Destinatário')
    receiver_name = models.CharField(max_length=200, default='', verbose_name='Nome/Razão Social do Destinatário')
    receiver_tax_id = models.CharField(max_length=20, default='', verbose_name='CNPJ/CPF Destinatário')
    receiver_state_registration = models.CharField(max_length=20, blank=True, null=True, verbose_name='Inscrição Estadual Destinatário')
    receiver_address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Endereço Destinatário')
    receiver_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número Destinatário')
    receiver_district = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bairro Destinatário')
    receiver_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Município Destinatário')
    receiver_city_code = models.CharField(max_length=7, blank=True, null=True, verbose_name='Código Município Destinatário')  # IBGE Code
    receiver_state = models.CharField(max_length=2, blank=True, null=True, verbose_name='UF Destinatário')
    receiver_zip_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='CEP Destinatário')
    receiver_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone Destinatário')
    receiver_email = models.EmailField(blank=True, null=True, verbose_name='Email Destinatário')
    
    # Dates
    issue_date = models.DateTimeField(verbose_name='Data de Emissão')
    due_date = models.DateField(null=True, blank=True, verbose_name='Data de Vencimento')
    authorization_date = models.DateTimeField(null=True, blank=True, verbose_name='Data de Autorização')
    
    # Financial
    total_products = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Total de Produtos')
    total_services = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Total de Serviços')
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Desconto')
    shipping = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Frete')
    insurance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Seguro')
    other_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Outras Despesas')
    
    # Taxes
    icms_base = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Base ICMS')
    icms_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor ICMS')
    ipi_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor IPI')
    pis_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor PIS')
    cofins_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor COFINS')
    iss_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor ISS')
    
    # Total
    total_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Total')
    
    # Additional Info
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    additional_info = models.TextField(blank=True, null=True, verbose_name='Informações Adicionais')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    protocol = models.CharField(max_length=50, blank=True, null=True, verbose_name='Protocolo')
    
    # SEFAZ-PR Specific Fields
    freight_mode = models.CharField(max_length=1, choices=FREIGHT_MODE_CHOICES, default='9', verbose_name='Modalidade do Frete')
    payment_indicator = models.CharField(max_length=1, choices=PAYMENT_INDICATOR_CHOICES, default='0', verbose_name='Indicador de Pagamento')
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES, default='99', verbose_name='Meio de Pagamento')
    payment_description = models.CharField(max_length=100, blank=True, null=True, verbose_name='Descrição do Pagamento')
    final_consumer_indicator = models.CharField(max_length=1, choices=FINAL_CONSUMER_CHOICES, default='0', verbose_name='Indicador Consumidor Final')
    presence_indicator = models.CharField(max_length=1, choices=PRESENCE_INDICATOR_CHOICES, default='0', verbose_name='Indicador de Presença')
    destination_indicator = models.CharField(max_length=1, choices=DESTINATION_INDICATOR_CHOICES, default='1', verbose_name='Indicador Destino')
    receiver_ie_indicator = models.CharField(max_length=1, choices=IE_INDICATOR_CHOICES, default='9', verbose_name='Indicador IE Destinatário')
    tax_regime = models.CharField(max_length=1, choices=TAX_REGIME_CHOICES, default='3', verbose_name='Código Regime Tributário')
    environment = models.CharField(max_length=1, choices=ENVIRONMENT_CHOICES, default='2', verbose_name='Ambiente')
    
    # Technical Responsible (Optional)
    tech_cnpj = models.CharField(max_length=14, blank=True, null=True, verbose_name='CNPJ Resp. Técnico')
    tech_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name='Contato Resp. Técnico')
    tech_email = models.EmailField(blank=True, null=True, verbose_name='Email Resp. Técnico')
    tech_phone = models.CharField(max_length=14, blank=True, null=True, verbose_name='Fone Resp. Técnico')
    
    # Files
    xml_file = models.FileField(upload_to='invoices/xml/%Y/%m/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='invoices/pdf/%Y/%m/', blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-number']
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'

    def __str__(self):
        return f"NF {self.number}/{self.series} - {self.client.name}"
    
    def save(self, *args, **kwargs):
        # Do not auto-generate access key - use NFeGenerator
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calculate the total invoice value"""
        total = (
            self.total_products +
            self.total_services +
            self.shipping +
            self.insurance +
            self.other_expenses +
            self.ipi_value -
            self.discount
        )
        self.total_value = total
        return total


class InvoiceItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('product', 'Produto'),
        ('service', 'Serviço'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='product')
    
    # Item Info
    code = models.CharField(max_length=50, verbose_name='Código')
    description = models.CharField(max_length=200, verbose_name='Descrição')
    ncm = models.CharField(max_length=10, blank=True, null=True, verbose_name='NCM')
    cfop = models.CharField(max_length=10, verbose_name='CFOP')
    unit = models.CharField(max_length=10, verbose_name='Unidade')
    
    # Quantity and Values
    quantity = models.DecimalField(max_digits=15, decimal_places=4, verbose_name='Quantidade')
    unit_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Unitário')
    total_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Total')
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Desconto')
    
    # Taxes
    icms_origin = models.CharField(max_length=1, default='0', verbose_name='Origem da Mercadoria', 
        help_text='0=Nacional, 1=Estrangeira Importação direta, 2=Estrangeira Mercado interno, etc.')
    icms_cst = models.CharField(max_length=3, default='00', verbose_name='CST ICMS',
        help_text='00, 10, 20, 30, 40, 41, 50, 51, 60, 70, 90 ou CSOSN para Simples Nacional')
    icms_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota ICMS')
    icms_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor ICMS')
    
    ipi_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota IPI')
    ipi_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor IPI')
    
    pis_cst = models.CharField(max_length=2, default='01', verbose_name='CST PIS',
        help_text='01-49, 50-56, 60-66, 70-75, 98-99')
    pis_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota PIS')
    pis_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor PIS')
    
    cofins_cst = models.CharField(max_length=2, default='01', verbose_name='CST COFINS',
        help_text='01-49, 50-56, 60-66, 70-75, 98-99')
    cofins_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota COFINS')
    cofins_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor COFINS')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item da Nota Fiscal'
        verbose_name_plural = 'Itens das Notas Fiscais'

    def __str__(self):
        return f"{self.code} - {self.description}"
    
    def save(self, *args, **kwargs):
        # Calcular total
        self.total_value = (self.quantity * self.unit_value) - self.discount
        super().save(*args, **kwargs)
