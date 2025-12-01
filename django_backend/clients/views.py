from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Client, ClientContact
from .serializers import ClientSerializer, ClientListSerializer, ClientContactSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    def get_queryset(self):
        queryset = Client.objects.all()
        
        # Filtro por status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filtro por tipo de pessoa
        person_type = self.request.query_params.get('person_type', None)
        if person_type:
            queryset = queryset.filter(person_type=person_type)
        
        # Busca por nome ou CPF/CNPJ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(trade_name__icontains=search) |
                Q(tax_id__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.select_related('created_by').prefetch_related('contacts')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_contact(self, request, pk=None):
        """Adicionar contato ao cliente"""
        client = self.get_object()
        serializer = ClientContactSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Alterar status do cliente"""
        client = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['active', 'inactive', 'suspended']:
            return Response(
                {'error': 'Status inválido. Use: active, inactive ou suspended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client.status = new_status
        client.save()
        
        return Response({
            'message': 'Status alterado com sucesso',
            'status': client.status
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas dos clientes"""
        total = Client.objects.count()
        active = Client.objects.filter(status='active').count()
        pf = Client.objects.filter(person_type='PF').count()
        pj = Client.objects.filter(person_type='PJ').count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'pessoa_fisica': pf,
            'pessoa_juridica': pj
        })


class ClientContactViewSet(viewsets.ModelViewSet):
    queryset = ClientContact.objects.all()
    serializer_class = ClientContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ClientContact.objects.all()
        client_id = self.request.query_params.get('client_id', None)
        
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        return queryset
