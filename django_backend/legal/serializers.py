from rest_framework import serializers
from .models import Lawyer, LegalProcess, Hearing, LegalContract, LegalDeadline


class LawyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lawyer
        fields = ['id', 'name', 'oab_number', 'oab_state', 'email', 'phone', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HearingSerializer(serializers.ModelSerializer):
    process_number = serializers.CharField(source='process.process_number', read_only=True)
    
    class Meta:
        model = Hearing
        fields = ['id', 'process', 'process_number', 'hearing_type', 'date', 'location', 'description', 'status', 'result', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LegalDeadlineSerializer(serializers.ModelSerializer):
    process_number = serializers.CharField(source='process.process_number', read_only=True)
    responsible_name = serializers.CharField(source='responsible.get_full_name', read_only=True)
    
    class Meta:
        model = LegalDeadline
        fields = ['id', 'process', 'process_number', 'title', 'description', 'due_date', 'priority', 'status', 'responsible', 'responsible_name', 'completion_date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LegalProcessSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    hearings_count = serializers.SerializerMethodField()
    deadlines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LegalProcess
        fields = [
            'id', 'process_number', 'process_type', 'title', 'description',
            'client', 'client_name', 'lawyer', 'lawyer_name', 'court',
            'status', 'priority', 'start_date', 'estimated_end_date', 'actual_end_date',
            'estimated_value', 'actual_value', 'notes',
            'hearings_count', 'deadlines_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'client_name', 'lawyer_name', 'created_by_name', 'hearings_count', 'deadlines_count']
    
    def get_hearings_count(self, obj):
        return obj.hearings.count()
    
    def get_deadlines_count(self, obj):
        return obj.deadlines.filter(status='pending').count()


class LegalProcessListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.name', read_only=True)
    
    class Meta:
        model = LegalProcess
        fields = ['id', 'process_number', 'process_type', 'title', 'client_name', 'lawyer_name', 'status', 'priority', 'start_date']


class LegalContractSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = LegalContract
        fields = [
            'id', 'contract_number', 'contract_type', 'title', 'description',
            'client', 'client_name', 'counterpart', 'counterpart_tax_id',
            'start_date', 'end_date', 'contract_value', 'status', 'file', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'client_name', 'created_by_name']


class LegalContractListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = LegalContract
        fields = ['id', 'contract_number', 'contract_type', 'title', 'client_name', 'status', 'start_date', 'end_date', 'contract_value']
