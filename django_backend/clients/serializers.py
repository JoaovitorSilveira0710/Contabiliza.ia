from rest_framework import serializers
from .models import Client, ClientContact


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = ['id', 'name', 'position', 'email', 'phone', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']


class ClientSerializer(serializers.ModelSerializer):
    contacts = ClientContactSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'person_type', 'name', 'trade_name', 'tax_id',
            'state_registration', 'municipal_registration',
            'email', 'phone', 'mobile',
            'zip_code', 'street', 'number', 'complement', 'neighborhood', 'city', 'state',
            'activity', 'status', 'tax_regime', 'payment_terms', 'credit_limit',
            'notes', 'contacts', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'contacts', 'created_by_name']

    def validate_tax_id(self, value):
        # Remove caracteres especiais
        value = ''.join(filter(str.isdigit, value))
        
        # Validação básica de CPF (11 dígitos) ou CNPJ (14 dígitos)
        if len(value) not in [11, 14]:
            raise serializers.ValidationError("CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos")
        
        return value


class ClientListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    class Meta:
        model = Client
        fields = ['id', 'person_type', 'name', 'trade_name', 'tax_id', 'email', 'phone', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
