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

    # Identification
    number = models.CharField(max_length=20, unique=True, verbose_name='Número')
    series = models.CharField(max_length=10, default='1', verbose_name='Série')
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE_CHOICES, default='nfe')
    access_key = models.CharField(max_length=44, blank=True, null=True, unique=True, verbose_name='Chave de Acesso')
    
    # Parties
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices', verbose_name='Cliente')
    issuer_name = models.CharField(max_length=200, verbose_name='Emitente')
    issuer_tax_id = models.CharField(max_length=20, verbose_name='CNPJ Emitente')
    
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
        if not self.access_key and self.invoice_type == 'nfe':
            # Gerar chave de acesso simplificada (em produção usar algoritmo oficial)
            self.access_key = str(uuid.uuid4().hex)[:44]
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calcula o valor total da nota"""
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
    icms_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota ICMS')
    icms_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor ICMS')
    ipi_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota IPI')
    ipi_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor IPI')
    pis_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Alíquota PIS')
    pis_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor PIS')
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
