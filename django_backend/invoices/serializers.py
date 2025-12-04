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
            'id', 'number', 'series', 'invoice_type', 'model_code', 'access_key',
            'operation_nature', 'operation_type', 'cfop',
            # Emitente
            'issuer_name', 'issuer_tax_id', 'issuer_fantasy_name', 'issuer_state_registration',
            'issuer_address', 'issuer_number', 'issuer_district', 'issuer_city', 'issuer_city_code',
            'issuer_state', 'issuer_zip_code', 'issuer_phone',
            # Destinatário
            'client', 'client_name', 'receiver_name', 'receiver_tax_id', 'receiver_state_registration',
            'receiver_address', 'receiver_number', 'receiver_district', 'receiver_city', 'receiver_city_code',
            'receiver_state', 'receiver_zip_code', 'receiver_phone', 'receiver_email',
            # Datas
            'issue_date', 'due_date', 'authorization_date',
            # Valores
            'total_products', 'total_services', 'discount', 'shipping', 'insurance', 'other_expenses',
            'icms_base', 'icms_value', 'ipi_value', 'pis_value', 'cofins_value', 'iss_value',
            'total_value', 'notes', 'additional_info',
            # Status e arquivos
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
            'number', 'series', 'invoice_type', 'model_code',
            'operation_nature', 'operation_type', 'cfop',
            # Emitente
            'issuer_name', 'issuer_tax_id', 'issuer_fantasy_name', 'issuer_state_registration',
            'issuer_address', 'issuer_number', 'issuer_district', 'issuer_city', 'issuer_city_code',
            'issuer_state', 'issuer_zip_code', 'issuer_phone',
            # Destinatário
            'client', 'receiver_name', 'receiver_tax_id', 'receiver_state_registration',
            'receiver_address', 'receiver_number', 'receiver_district', 'receiver_city', 'receiver_city_code',
            'receiver_state', 'receiver_zip_code', 'receiver_phone', 'receiver_email',
            # Datas
            'issue_date', 'due_date',
            # Valores
            'discount', 'shipping', 'insurance', 'other_expenses',
            'icms_base', 'icms_value', 'ipi_value', 'pis_value', 'cofins_value', 'iss_value',
            'notes', 'additional_info', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Check if it is an interstate operation
        issuer_state = validated_data.get('issuer_state', '').upper()
        receiver_state = validated_data.get('receiver_state', '').upper()
        is_interstate = issuer_state != receiver_state and issuer_state and receiver_state
        
        # If interstate operation, zero out ICMS or apply interstate rate
        if is_interstate:
            # For interstate operations, ICMS follows specific rules
            # Here we zero out to simplify (in practice, apply rate of 4%, 7% or 12%)
            validated_data['icms_value'] = 0
            validated_data['icms_base'] = 0
            # Update notes field
            obs = validated_data.get('notes', '') or ''
            if obs:
                obs += '\n'
            obs += f'INTERSTATE OPERATION: {issuer_state} -> {receiver_state}. ICMS not highlighted per legislation.'
            validated_data['notes'] = obs
        
        invoice = Invoice.objects.create(**validated_data)
        
        # Create items
        total_products = 0
        total_services = 0
        
        for item_data in items_data:
            # If interstate, also zero out ICMS for items
            if is_interstate:
                item_data['icms_value'] = 0
                item_data['icms_rate'] = 0
            
            item = InvoiceItem.objects.create(invoice=invoice, **item_data)
            if item.item_type == 'product':
                total_products += item.total_value
            else:
                total_services += item.total_value
        
        # Update totals
        invoice.total_products = total_products
        invoice.total_services = total_services
        invoice.calculate_total()
        invoice.save()
        
        return invoice
