from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
import requests
from django.db.models import Q
from .models import Client, Farm
from .serializers import ClientSerializer, ClientListSerializer, FarmSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
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


class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cnpj_lookup(request, cnpj):
    """Buscar dados de CNPJ em tempo real via BrasilAPI e mapear para campos de Client.
    """
    cnpj_digits = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_digits) != 14:
        return Response({'error': 'CNPJ inválido. Deve ter 14 dígitos.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        resp = requests.get(f'https://brasilapi.com.br/api/cnpj/v1/{cnpj_digits}', timeout=10)
        if resp.status_code != 200:
            return Response({'error': 'Não foi possível consultar o CNPJ.'}, status=status.HTTP_400_BAD_REQUEST)
        data = resp.json()
    except Exception:
        return Response({'error': 'Falha na consulta de CNPJ.'}, status=status.HTTP_400_BAD_REQUEST)

    # Mapear campos para o nosso cliente
    mapped = {
        'person_type': 'PJ',
        'name': data.get('razao_social') or data.get('nome_fantasia') or '',
        'trade_name': data.get('nome_fantasia') or '',
        'tax_id': cnpj_digits,
        'email': (data.get('email') or '').lower(),
        'phone': (data.get('ddd_telefone_1') or '').replace('\n', '').replace(' ', ''),
        'zip_code': (data.get('cep') or '').replace('-', ''),
        'street': data.get('logradouro') or '',
        'number': data.get('numero') or '',
        'complement': data.get('complemento') or '',
        'neighborhood': data.get('bairro') or '',
        'city': data.get('municipio') or '',
        'state': data.get('uf') or '',
        'state_registration': data.get('inscricao_estadual') or None,
        'municipal_registration': None,
        'status': 'active'
    }

    return Response(mapped)
