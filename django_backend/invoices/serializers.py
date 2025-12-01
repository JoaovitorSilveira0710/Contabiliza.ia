from rest_framework import serializers
from .models import Invoice, InvoiceItem
from clients.serializers import ClientListSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'item_type', 'code', 'description', 'ncm', 'cfop', 'unit',
            'quantity', 'unit_value', 'total_value', 'discount',
            'icms_rate', 'icms_value', 'ipi_rate', 'ipi_value',
            'pis_rate', 'pis_value', 'cofins_rate', 'cofins_value'
        ]
        read_only_fields = ['id', 'total_value']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'number', 'series', 'invoice_type', 'access_key',
            'client', 'client_name', 'issuer_name', 'issuer_tax_id',
            'issue_date', 'due_date', 'authorization_date',
            'total_products', 'total_services', 'discount', 'shipping', 'insurance', 'other_expenses',
            'icms_base', 'icms_value', 'ipi_value', 'pis_value', 'cofins_value', 'iss_value',
            'total_value', 'notes', 'additional_info',
            'status', 'protocol', 'xml_file', 'pdf_file',
            'items', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'access_key', 'created_at', 'updated_at', 'items', 'client_name', 'created_by_name']


class InvoiceListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'number', 'series', 'invoice_type', 'client', 'client_name', 'issue_date', 'total_value', 'status']
        read_only_fields = ['id']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = [
            'number', 'series', 'invoice_type', 'client', 'issuer_name', 'issuer_tax_id',
            'issue_date', 'due_date', 'discount', 'shipping', 'insurance', 'other_expenses',
            'icms_base', 'icms_value', 'ipi_value', 'pis_value', 'cofins_value', 'iss_value',
            'notes', 'additional_info', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        
        # Criar itens
        total_products = 0
        total_services = 0
        
        for item_data in items_data:
            item = InvoiceItem.objects.create(invoice=invoice, **item_data)
            if item.item_type == 'product':
                total_products += item.total_value
            else:
                total_services += item.total_value
        
        # Atualizar totais
        invoice.total_products = total_products
        invoice.total_services = total_services
        invoice.calculate_total()
        invoice.save()
        
        return invoice
