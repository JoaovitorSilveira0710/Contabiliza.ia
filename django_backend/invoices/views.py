from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer, InvoiceListSerializer, InvoiceCreateSerializer, InvoiceItemSerializer
from .services.xml_generator import NFeGenerator
from .services.pdf_generator import InvoicePDFGenerator
from .services.backup_service import backup_invoice_files


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        queryset = Invoice.objects.all()
        
        # Filtro por status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filtro por tipo
        invoice_type = self.request.query_params.get('invoice_type', None)
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        
        # Filtro por cliente
        client_id = self.request.query_params.get('client_id', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filtro por período
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(issue_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(issue_date__lte=end_date)
        
        # Busca por número
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(client__name__icontains=search) |
                Q(access_key__icontains=search)
            )
        
        return queryset.select_related('client', 'created_by').prefetch_related('items')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_xml(self, request, pk=None):
        """Gerar XML da NF-e"""
        invoice = self.get_object()
        
        if invoice.invoice_type not in ['nfe', 'nfce']:
            return Response(
                {'error': 'Geração de XML disponível apenas para NF-e e NFC-e'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generator = NFeGenerator(invoice)
            generator.generate_xml()
            # Backup após geração
            backup_invoice_files(invoice)
            return Response({
                'message': 'XML gerado com sucesso',
                'xml_file': request.build_absolute_uri(invoice.xml_file.url)
            })
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar XML: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Gerar PDF da DANFE"""
        invoice = self.get_object()
        
        try:
            generator = InvoicePDFGenerator(invoice)
            generator.generate_pdf()
            # Backup após geração
            backup_invoice_files(invoice)
            return Response({
                'message': 'PDF gerado com sucesso',
                'pdf_file': request.build_absolute_uri(invoice.pdf_file.url)
            })
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_xml(self, request, pk=None):
        """Download do XML"""
        invoice = self.get_object()
        
        if not invoice.xml_file:
            return Response(
                {'error': 'XML não gerado. Use a ação generate_xml primeiro'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            invoice.xml_file.open('rb'),
            as_attachment=True,
            filename=f"NFe{invoice.number}_{invoice.series}.xml"
        )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download do PDF"""
        invoice = self.get_object()
        
        if not invoice.pdf_file:
            return Response(
                {'error': 'PDF não gerado. Use a ação generate_pdf primeiro'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            invoice.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"DANFE_{invoice.number}_{invoice.series}.pdf"
        )
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Alterar status da nota"""
        invoice = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['draft', 'pending', 'authorized', 'cancelled', 'denied']:
            return Response(
                {'error': 'Status inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = new_status
        
        if new_status == 'authorized':
            invoice.authorization_date = datetime.now()
        
        invoice.save()
        
        return Response({
            'message': 'Status alterado com sucesso',
            'status': invoice.status
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar nota fiscal"""
        invoice = self.get_object()
        
        if invoice.status == 'cancelled':
            return Response(
                {'error': 'Nota já está cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invoice.status != 'authorized':
            return Response(
                {'error': 'Apenas notas autorizadas podem ser canceladas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'cancelled'
        invoice.save()
        
        return Response({'message': 'Nota fiscal cancelada com sucesso'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas das notas fiscais"""
        # Total por status
        by_status = Invoice.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('total_value')
        )
        
        # Total do mês atual
        today = datetime.now()
        first_day = today.replace(day=1)
        month_invoices = Invoice.objects.filter(
            issue_date__gte=first_day,
            status='authorized'
        ).aggregate(
            count=Count('id'),
            total=Sum('total_value')
        )
        
        # Últimas 30 dias
        thirty_days_ago = today - timedelta(days=30)
        recent_invoices = Invoice.objects.filter(
            issue_date__gte=thirty_days_ago
        ).aggregate(
            count=Count('id'),
            total=Sum('total_value')
        )
        
        return Response({
            'by_status': list(by_status),
            'current_month': month_invoices,
            'last_30_days': recent_invoices
        })


class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = InvoiceItem.objects.all()
        invoice_id = self.request.query_params.get('invoice_id', None)
        
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)
        
        return queryset
