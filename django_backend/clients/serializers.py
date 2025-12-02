from rest_framework import serializers
from .models import Client, ClientContact, Farm


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


class FarmSerializer(serializers.ModelSerializer):
    owners_cpfs = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'tax_id', 'zip_code', 'street', 'number', 'complement', 'neighborhood',
            'city', 'state', 'area_ha', 'matricula', 'car', 'itr', 'ccir', 'owners', 'owners_cpfs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_tax_id(self, value):
        if value:
            digits = ''.join(filter(str.isdigit, value))
            if len(digits) not in [11, 14]:
                raise serializers.ValidationError('CPF deve ter 11 dígitos ou CNPJ 14 dígitos')
            return digits
        return value

    def create(self, validated_data):
        owners_cpfs = validated_data.pop('owners_cpfs', [])
        farm = super().create(validated_data)
        if owners_cpfs:
            # Map CPFs to PF clients and link
            cpf_digits = [ ''.join(filter(str.isdigit, c)) for c in owners_cpfs ]
            owners = Client.objects.filter(person_type='PF', tax_id__in=cpf_digits)
            farm.owners.set(owners)
            # Append observation to owners' notes
            obs_parts = [
                f"Fazenda: {farm.name}",
                f"{farm.city}/{farm.state}" if farm.city and farm.state else '',
                f"Matrícula: {farm.matricula}" if farm.matricula else '',
                f"CAR: {farm.car}" if farm.car else '',
                f"ITR: {farm.itr}" if farm.itr else '',
                f"CCIR: {farm.ccir}" if farm.ccir else '',
                f"Área: {farm.area_ha} ha" if farm.area_ha else '',
            ]
            obs_line = ' — '.join([p for p in obs_parts if p])
            for owner in owners:
                owner.notes = (owner.notes + "\n" + obs_line) if owner.notes else obs_line
                owner.save(update_fields=['notes'])
        return farm
