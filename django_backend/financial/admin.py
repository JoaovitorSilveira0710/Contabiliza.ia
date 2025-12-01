from django.contrib import admin
from .models import (
    FinancialCategory, BankAccount, FinancialTransaction,
    AccountsPayable, AccountsReceivable, CashFlow
)


@admin.register(FinancialCategory)
class FinancialCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'is_active', 'created_at')
    list_filter = ('category_type', 'is_active')
    search_fields = ('name', 'description')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'bank_name', 'current_balance', 'is_active')
    list_filter = ('account_type', 'is_active')
    search_fields = ('name', 'bank_name', 'account_number')
    readonly_fields = ('current_balance', 'created_at', 'updated_at')


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'transaction_type', 'amount', 'final_amount', 'due_date', 'status')
    list_filter = ('transaction_type', 'status', 'category', 'due_date')
    search_fields = ('description', 'document_number')
    readonly_fields = ('final_amount', 'created_at', 'updated_at')
    date_hierarchy = 'due_date'


@admin.register(AccountsPayable)
class AccountsPayableAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'supplier_tax_id', 'transaction')
    search_fields = ('supplier_name', 'supplier_tax_id')


@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(admin.ModelAdmin):
    list_display = ('customer', 'invoice_number', 'transaction')
    search_fields = ('customer__name', 'invoice_number')


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ('date', 'opening_balance', 'total_revenue', 'total_expense', 'closing_balance')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
