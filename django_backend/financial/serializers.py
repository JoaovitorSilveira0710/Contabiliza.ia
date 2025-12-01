from rest_framework import serializers
from .models import (
    FinancialCategory, BankAccount, FinancialTransaction,
    AccountsPayable, AccountsReceivable, CashFlow
)
from clients.serializers import ClientListSerializer


class FinancialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialCategory
        fields = ['id', 'name', 'category_type', 'description', 'color', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id', 'name', 'account_type', 'bank_name', 'agency', 'account_number',
            'initial_balance', 'current_balance', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_balance', 'created_at', 'updated_at']


class FinancialTransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'transaction_type', 'description', 'category', 'category_name',
            'client', 'client_name', 'account', 'account_name', 'destination_account',
            'amount', 'discount', 'interest', 'fine', 'final_amount',
            'due_date', 'payment_date', 'competence_date',
            'payment_method', 'document_number', 'status',
            'is_recurring', 'recurrence_frequency', 'notes', 'attachment',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'final_amount', 'created_at', 'updated_at', 'category_name', 'account_name', 'client_name', 'created_by_name']


class FinancialTransactionListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'transaction_type', 'description', 'category_name', 'account_name',
            'amount', 'final_amount', 'due_date', 'payment_date', 'status'
        ]


class AccountsPayableSerializer(serializers.ModelSerializer):
    transaction = FinancialTransactionSerializer(read_only=True)
    
    class Meta:
        model = AccountsPayable
        fields = ['id', 'transaction', 'supplier_name', 'supplier_tax_id']


class AccountsReceivableSerializer(serializers.ModelSerializer):
    transaction = FinancialTransactionSerializer(read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = AccountsReceivable
        fields = ['id', 'transaction', 'customer', 'customer_name', 'invoice_number']


class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlow
        fields = [
            'id', 'date', 'opening_balance', 'total_revenue', 'total_expense',
            'closing_balance', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
