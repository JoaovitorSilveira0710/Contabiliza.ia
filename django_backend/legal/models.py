from django.db import models
from django.conf import settings
from clients.models import Client


class Lawyer(models.Model):
    """Advogado"""
    name = models.CharField('Nome', max_length=200)
    oab_number = models.CharField('Número OAB', max_length=50)
    oab_state = models.CharField('Estado OAB', max_length=2)
    email = models.EmailField('E-mail')
    phone = models.CharField('Telefone', max_length=20)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Advogado'
        verbose_name_plural = 'Advogados'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - OAB {self.oab_number}/{self.oab_state}"


class LegalProcess(models.Model):
    """Processo Jurídico"""
    PROCESS_TYPES = [
        ('civil', 'Cível'),
        ('labor', 'Trabalhista'),
        ('tax', 'Tributário'),
        ('corporate', 'Empresarial'),
        ('administrative', 'Administrativo'),
        ('other', 'Outro'),
    ]
    
    PROCESS_STATUS = [
        ('active', 'Ativo'),
        ('suspended', 'Suspenso'),
        ('archived', 'Arquivado'),
        ('finished', 'Finalizado'),
    ]
    
    PRIORITY = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    process_number = models.CharField('Número do Processo', max_length=100, unique=True)
    process_type = models.CharField('Tipo', max_length=50, choices=PROCESS_TYPES)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='legal_processes', verbose_name='Cliente')
    lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, related_name='processes', verbose_name='Advogado')
    court = models.CharField('Comarca/Tribunal', max_length=200)
    status = models.CharField('Status', max_length=50, choices=PROCESS_STATUS, default='active')
    priority = models.CharField('Prioridade', max_length=20, choices=PRIORITY, default='medium')
    start_date = models.DateField('Data de Início')
    estimated_end_date = models.DateField('Previsão de Término', null=True, blank=True)
    actual_end_date = models.DateField('Data de Término', null=True, blank=True)
    estimated_value = models.DecimalField('Valor Estimado', max_digits=15, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField('Valor Real', max_digits=15, decimal_places=2, null=True, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_legal_processes')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Processo Jurídico'
        verbose_name_plural = 'Processos Jurídicos'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.process_number} - {self.title}"


class Hearing(models.Model):
    """Audiência"""
    HEARING_TYPES = [
        ('conciliation', 'Conciliação'),
        ('instruction', 'Instrução'),
        ('judgment', 'Julgamento'),
        ('other', 'Outra'),
    ]
    
    STATUS = [
        ('scheduled', 'Agendada'),
        ('completed', 'Realizada'),
        ('cancelled', 'Cancelada'),
        ('postponed', 'Adiada'),
    ]
    
    process = models.ForeignKey(LegalProcess, on_delete=models.CASCADE, related_name='hearings', verbose_name='Processo')
    hearing_type = models.CharField('Tipo', max_length=50, choices=HEARING_TYPES)
    date = models.DateTimeField('Data e Hora')
    location = models.CharField('Local', max_length=300)
    description = models.TextField('Descrição', blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS, default='scheduled')
    result = models.TextField('Resultado', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Audiência'
        verbose_name_plural = 'Audiências'
        ordering = ['date']

    def __str__(self):
        return f"{self.process.process_number} - {self.hearing_type} - {self.date.strftime('%d/%m/%Y %H:%M')}"


class LegalContract(models.Model):
    """Contrato"""
    CONTRACT_TYPES = [
        ('service', 'Prestação de Serviço'),
        ('partnership', 'Parceria'),
        ('rental', 'Locação'),
        ('purchase', 'Compra e Venda'),
        ('confidentiality', 'Confidencialidade'),
        ('employment', 'Trabalho'),
        ('other', 'Outro'),
    ]
    
    STATUS = [
        ('draft', 'Minuta'),
        ('under_review', 'Em Análise'),
        ('active', 'Vigente'),
        ('expired', 'Expirado'),
        ('terminated', 'Rescindido'),
    ]
    
    contract_number = models.CharField('Número do Contrato', max_length=100, unique=True)
    contract_type = models.CharField('Tipo', max_length=50, choices=CONTRACT_TYPES)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='legal_contracts', verbose_name='Cliente')
    counterpart = models.CharField('Outra Parte', max_length=200)
    counterpart_tax_id = models.CharField('CPF/CNPJ Outra Parte', max_length=20, blank=True)
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término', null=True, blank=True)
    contract_value = models.DecimalField('Valor do Contrato', max_digits=15, decimal_places=2)
    status = models.CharField('Status', max_length=50, choices=STATUS, default='draft')
    file = models.FileField('Arquivo', upload_to='contracts/', null=True, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.contract_number} - {self.title}"


class LegalDeadline(models.Model):
    """Prazo Jurídico"""
    PRIORITY = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS = [
        ('pending', 'Pendente'),
        ('completed', 'Concluído'),
        ('overdue', 'Atrasado'),
        ('cancelled', 'Cancelado'),
    ]
    
    process = models.ForeignKey(LegalProcess, on_delete=models.CASCADE, related_name='deadlines', verbose_name='Processo', null=True, blank=True)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    due_date = models.DateField('Data de Vencimento')
    priority = models.CharField('Prioridade', max_length=20, choices=PRIORITY, default='medium')
    status = models.CharField('Status', max_length=20, choices=STATUS, default='pending')
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='legal_deadlines', verbose_name='Responsável')
    completion_date = models.DateField('Data de Conclusão', null=True, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Prazo Jurídico'
        verbose_name_plural = 'Prazos Jurídicos'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.due_date.strftime('%d/%m/%Y')}"
