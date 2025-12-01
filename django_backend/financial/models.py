from django.db import models
from django.conf import settings
from clients.models import Client
from decimal import Decimal


class FinancialCategory(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('revenue', 'Receita'),
        ('expense', 'Despesa'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES, verbose_name='Tipo')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name='Cor')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoria Financeira'
        verbose_name_plural = 'Categorias Financeiras'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class BankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('checking', 'Conta Corrente'),
        ('savings', 'Poupança'),
        ('investment', 'Investimento'),
        ('cash', 'Dinheiro'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, verbose_name='Tipo')
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Banco')
    agency = models.CharField(max_length=20, blank=True, null=True, verbose_name='Agência')
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número da Conta')
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Saldo Inicial')
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Saldo Atual')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_account_type_display()}"


class FinancialTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('revenue', 'Receita'),
        ('expense', 'Despesa'),
        ('transfer', 'Transferência'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('received', 'Recebido'),
        ('cancelled', 'Cancelado'),
        ('overdue', 'Vencido'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('money', 'Dinheiro'),
        ('debit_card', 'Cartão de Débito'),
        ('credit_card', 'Cartão de Crédito'),
        ('bank_transfer', 'Transferência Bancária'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('check', 'Cheque'),
        ('other', 'Outro'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name='Tipo')
    description = models.CharField(max_length=200, verbose_name='Descrição')
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name='transactions', verbose_name='Categoria')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    
    # Bank Accounts
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='transactions', verbose_name='Conta')
    destination_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, null=True, blank=True, related_name='transfers_received', verbose_name='Conta Destino')
    
    # Values
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Desconto')
    interest = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Juros')
    fine = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Multa')
    final_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Final')
    
    # Dates
    due_date = models.DateField(verbose_name='Data de Vencimento')
    payment_date = models.DateField(null=True, blank=True, verbose_name='Data de Pagamento')
    competence_date = models.DateField(verbose_name='Data de Competência')
    
    # Payment Info
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True, verbose_name='Forma de Pagamento')
    document_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número do Documento')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_recurring = models.BooleanField(default=False, verbose_name='Recorrente')
    recurrence_frequency = models.CharField(max_length=20, blank=True, null=True, verbose_name='Frequência')  # monthly, weekly, etc
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    attachment = models.FileField(upload_to='financial/attachments/%Y/%m/', blank=True, null=True, verbose_name='Anexo')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='financial_transactions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transação Financeira'
        verbose_name_plural = 'Transações Financeiras'
        ordering = ['-due_date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.description} - R$ {self.amount}"
    
    def save(self, *args, **kwargs):
        # Calcular valor final
        if self.transaction_type == 'expense':
            self.final_amount = self.amount - self.discount + self.interest + self.fine
        else:
            self.final_amount = self.amount - self.discount
        
        super().save(*args, **kwargs)
        
        # Atualizar saldo da conta se pago/recebido
        if self.status in ['paid', 'received'] and self.payment_date:
            if self.transaction_type == 'revenue':
                self.account.current_balance += self.final_amount
            elif self.transaction_type == 'expense':
                self.account.current_balance -= self.final_amount
            elif self.transaction_type == 'transfer' and self.destination_account:
                self.account.current_balance -= self.final_amount
                self.destination_account.current_balance += self.final_amount
                self.destination_account.save()
            self.account.save()


class AccountsPayable(models.Model):
    """Contas a Pagar"""
    transaction = models.OneToOneField(FinancialTransaction, on_delete=models.CASCADE, related_name='payable')
    supplier_name = models.CharField(max_length=200, verbose_name='Fornecedor')
    supplier_tax_id = models.CharField(max_length=20, blank=True, null=True, verbose_name='CPF/CNPJ Fornecedor')
    
    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
    
    def __str__(self):
        return f"Pagar: {self.supplier_name} - R$ {self.transaction.amount}"


class AccountsReceivable(models.Model):
    """Contas a Receber"""
    transaction = models.OneToOneField(FinancialTransaction, on_delete=models.CASCADE, related_name='receivable')
    customer = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='receivables')
    invoice_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número da Nota')
    
    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
    
    def __str__(self):
        return f"Receber: {self.customer.name} - R$ {self.transaction.amount}"


class CashFlow(models.Model):
    """Registro de Fluxo de Caixa"""
    date = models.DateField(verbose_name='Data')
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Saldo Inicial')
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Total Receitas')
    total_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Total Despesas')
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Saldo Final')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fluxo de Caixa'
        verbose_name_plural = 'Fluxo de Caixa'
        ordering = ['-date']
        unique_together = ['date']
    
    def __str__(self):
        return f"Fluxo de Caixa - {self.date}"
