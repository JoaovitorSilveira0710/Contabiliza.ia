from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.db.models import Q, Sum, Count
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer, InvoiceListSerializer, InvoiceCreateSerializer, InvoiceItemSerializer
from .services.xml_generator import NFeGenerator
from .services.pdf_generator import InvoicePDFGenerator
from .services.danfe_sefaz_pr import DANFESefazGenerator
from .services.nfe_xml_generator import NFeXMLGenerator
from .services.sefaz_integration import SefazIntegration
from .services.backup_service import backup_invoice_files
import os


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
        
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        invoice_type = self.request.query_params.get('invoice_type', None)
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        
        client_id = self.request.query_params.get('client_id', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(issue_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(issue_date__lte=end_date)
        
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
    def generate_nfe_complete(self, request, pk=None):
        """Generate XML and PDF of NF-e in SEFAZ standard and save to storage"""
        invoice = self.get_object()
        
        try:
            xml_generator = NFeXMLGenerator(invoice)
            xml_content = xml_generator.generate()
            chave_acesso = xml_generator._generate_chave_acesso()
            
            xml_filename = f"{chave_acesso}-nfe.xml"
            xml_path = f"invoices/xml/{datetime.now().year}/{datetime.now().month:02d}/{xml_filename}"
            invoice.xml_file.save(xml_filename, ContentFile(xml_content.encode('utf-8')), save=False)
            
            invoice.access_key = chave_acesso
            
            sefaz = SefazIntegration(uf=invoice.issuer_state or 'PR', ambiente='homologacao')
            validacao = sefaz.validar_xml_nfe(xml_content)
            
            if not validacao['valido']:
                return Response({
                    'error': 'Invalid XML',
                    'erros': validacao['erros']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if invoice.issuer_state == 'PR':
                pdf_generator = DANFESefazGenerator(invoice)
            else:
                pdf_generator = InvoicePDFGenerator(invoice)
            
            pdf_content = pdf_generator.generate()
            
            pdf_filename = f"{chave_acesso}-danfe.pdf"
            pdf_path = f"invoices/pdf/{datetime.now().year}/{datetime.now().month:02d}/{pdf_filename}"
            invoice.pdf_file.save(pdf_filename, ContentFile(pdf_content), save=False)
            
            invoice.status = 'pending'
            invoice.save()
            
            backup_invoice_files(invoice)
            
            return Response({
                'message': 'NF-e generated successfully',
                'chave_acesso': chave_acesso,
                'xml_file': request.build_absolute_uri(invoice.xml_file.url) if invoice.xml_file else None,
                'pdf_file': request.build_absolute_uri(invoice.pdf_file.url) if invoice.pdf_file else None,
                'validacao': validacao,
                'status': invoice.status
            })
            
        except Exception as e:
            return Response({
                'error': f'Error generating NF-e: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def authorize_sefaz(self, request, pk=None):
        """Send NF-e for authorization in SEFAZ"""
        invoice = self.get_object()
        
        if not invoice.xml_file:
            return Response({
                'error': 'XML not generated. Use generate_nfe_complete first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if invoice.status not in ['pending', 'draft']:
            return Response({
                'error': f'Invoice with status {invoice.status} cannot be authorized'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invoice.xml_file.open('r')
            xml_content = invoice.xml_file.read()
            if isinstance(xml_content, bytes):
                xml_content = xml_content.decode('utf-8')
            invoice.xml_file.close()
            
            ambiente = invoice.environment or '2'
            sefaz = SefazIntegration(
                uf=invoice.issuer_state or 'PR',
                ambiente='homologacao' if ambiente == '2' else 'producao'
            )
            
            resultado = sefaz.autorizar_nfe(xml_content)
            
            if resultado['sucesso']:
                invoice.status = 'authorized'
                invoice.protocol = resultado.get('protocolo')
                invoice.authorization_date = datetime.now()
                invoice.save()
                
                return Response({
                    'message': 'NF-e authorized successfully',
                    'codigo': resultado.get('codigo'),
                    'protocolo': resultado.get('protocolo'),
                    'chave_acesso': resultado.get('chave_acesso'),
                    'observacao': resultado.get('observacao')
                })
            else:
                invoice.status = 'denied'
                invoice.save()
                
                return Response({
                    'error': 'Authorization denied by SEFAZ',
                    'codigo': resultado.get('codigo'),
                    'mensagem': resultado.get('mensagem')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'Error authorizing NF-e: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def generate_xml(self, request, pk=None):
        """Generate NF-e XML"""
        invoice = self.get_object()
        
        if invoice.invoice_type not in ['nfe', 'nfce']:
            return Response(
                {'error': 'XML generation available only for NF-e and NFC-e'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generator = NFeGenerator(invoice)
            generator.generate_xml()
            backup_invoice_files(invoice)
            return Response({
                'message': 'XML generated successfully',
                'xml_file': request.build_absolute_uri(invoice.xml_file.url)
            })
        except Exception as e:
            return Response(
                {'error': f'Error generating XML: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate DANFE PDF"""
        invoice = self.get_object()
        
        try:
            if invoice.issuer_state == 'PR' or request.query_params.get('layout') == 'pr':
                generator = DANFESefazGenerator(invoice)
            else:
                generator = InvoicePDFGenerator(invoice)
            
            generator.generate_pdf()
            backup_invoice_files(invoice)
            return Response({
                'message': 'PDF generated successfully',
                'pdf_file': request.build_absolute_uri(invoice.pdf_file.url)
            })
        except Exception as e:
            return Response(
                {'error': f'Error generating PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_xml(self, request, pk=None):
        """Download XML"""
        invoice = self.get_object()
        
        if not invoice.xml_file:
            return Response(
                {'error': 'XML not generated. Use generate_xml action first'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            invoice.xml_file.open('rb'),
            as_attachment=True,
            filename=f"NFe{invoice.number}_{invoice.series}.xml"
        )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download PDF"""
        invoice = self.get_object()
        
        if not invoice.pdf_file:
            return Response(
                {'error': 'PDF not generated. Use generate_pdf action first'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            invoice.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"DANFE_{invoice.number}_{invoice.series}.pdf"
        )
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Change invoice status"""
        invoice = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['draft', 'pending', 'authorized', 'cancelled', 'denied']:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = new_status
        
        if new_status == 'authorized':
            invoice.authorization_date = datetime.now()
        
        invoice.save()
        
        return Response({
            'message': 'Status changed successfully',
            'status': invoice.status
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel invoice"""
        invoice = self.get_object()
        
        if invoice.status == 'cancelled':
            return Response(
                {'error': 'Invoice is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invoice.status != 'authorized':
            return Response(
                {'error': 'Only authorized invoices can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'cancelled'
        invoice.save()
        
        return Response({'message': 'Invoice successfully cancelled'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Invoice statistics"""
        # Total by status
        by_status = Invoice.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('total_value')
        )
        
        # Total for current month
        today = datetime.now()
        first_day = today.replace(day=1)
        month_invoices = Invoice.objects.filter(
            issue_date__gte=first_day,
            status='authorized'
        ).aggregate(
            count=Count('id'),
            total=Sum('total_value')
        )
        
        # Last 30 days
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
