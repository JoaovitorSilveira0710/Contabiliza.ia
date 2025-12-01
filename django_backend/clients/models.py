from django.db import models
from django.conf import settings


class Client(models.Model):
    PERSON_TYPE_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('suspended', 'Suspenso'),
    ]

    # Basic Information
    person_type = models.CharField(max_length=2, choices=PERSON_TYPE_CHOICES, default='PF')
    name = models.CharField(max_length=200, verbose_name='Nome/Razão Social')
    trade_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nome Fantasia')
    
    # Documents
    tax_id = models.CharField(max_length=20, unique=True, verbose_name='CPF/CNPJ')
    state_registration = models.CharField(max_length=20, blank=True, null=True, verbose_name='Inscrição Estadual')
    municipal_registration = models.CharField(max_length=20, blank=True, null=True, verbose_name='Inscrição Municipal')
    
    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    
    # Address
    zip_code = models.CharField(max_length=10, verbose_name='CEP')
    street = models.CharField(max_length=200, verbose_name='Logradouro')
    number = models.CharField(max_length=20, verbose_name='Número')
    complement = models.CharField(max_length=100, blank=True, null=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, verbose_name='Bairro')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    state = models.CharField(max_length=2, verbose_name='Estado')
    
    # Business Info
    activity = models.CharField(max_length=200, blank=True, null=True, verbose_name='Atividade Principal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Accounting Settings
    tax_regime = models.CharField(max_length=50, blank=True, null=True, verbose_name='Regime Tributário')
    payment_terms = models.IntegerField(default=30, verbose_name='Prazo de Pagamento (dias)')
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Limite de Crédito')
    
    # Metadata
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='clients_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.name} - {self.tax_id}"


class ClientContact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100, verbose_name='Nome')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cargo')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_main = models.BooleanField(default=False, verbose_name='Contato Principal')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contato do Cliente'
        verbose_name_plural = 'Contatos dos Clientes'

    def __str__(self):
        return f"{self.name} - {self.client.name}"
