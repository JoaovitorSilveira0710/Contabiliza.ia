from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from .models import Lawyer, LegalProcess, Hearing, LegalContract, LegalDeadline
from .serializers import (
    LawyerSerializer, LegalProcessSerializer, LegalProcessListSerializer,
    HearingSerializer, LegalContractSerializer, LegalContractListSerializer,
    LegalDeadlineSerializer
)
from .services import CourtIntegrationService


class LawyerViewSet(viewsets.ModelViewSet):
    queryset = Lawyer.objects.all()
    serializer_class = LawyerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Lawyer.objects.filter(is_active=True)
        return queryset.order_by('name')


class LegalProcessViewSet(viewsets.ModelViewSet):
    queryset = LegalProcess.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LegalProcessListSerializer
        return LegalProcessSerializer
    
    def get_queryset(self):
        queryset = LegalProcess.objects.all()
        
        # Filtros
        process_type = self.request.query_params.get('process_type', None)
        status_param = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        lawyer_id = self.request.query_params.get('lawyer_id', None)
        client_id = self.request.query_params.get('client_id', None)
        search = self.request.query_params.get('search', None)
        
        if process_type:
            queryset = queryset.filter(process_type=process_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if priority:
            queryset = queryset.filter(priority=priority)
        if lawyer_id:
            queryset = queryset.filter(lawyer_id=lawyer_id)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if search:
            queryset = queryset.filter(
                Q(process_number__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('client', 'lawyer', 'created_by').order_by('-start_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Alterar status do processo"""
        process = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Campo status é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        process.status = new_status
        
        if new_status == 'finished' and not process.actual_end_date:
            process.actual_end_date = datetime.now().date()
        
        process.save()
        
        return Response({
            'message': 'Status atualizado com sucesso',
            'process': LegalProcessSerializer(process).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de processos"""
        total = LegalProcess.objects.count()
        by_status = LegalProcess.objects.values('status').annotate(count=Count('id'))
        by_type = LegalProcess.objects.values('process_type').annotate(count=Count('id'))
        by_priority = LegalProcess.objects.values('priority').annotate(count=Count('id'))
        
        # Valor total
        total_estimated = LegalProcess.objects.aggregate(total=Sum('estimated_value'))['total'] or 0
        total_actual = LegalProcess.objects.aggregate(total=Sum('actual_value'))['total'] or 0
        
        return Response({
            'total': total,
            'by_status': list(by_status),
            'by_type': list(by_type),
            'by_priority': list(by_priority),
            'total_estimated_value': str(total_estimated),
            'total_actual_value': str(total_actual)
        })
    
    @action(detail=False, methods=['post'])
    def search_court(self, request):
        """
        Busca informações de processo nos tribunais
        Recebe: { "process_number": "0000000-00.0000.0.00.0000" }
        """
        process_number = request.data.get('process_number')
        
        if not process_number:
            return Response(
                {'error': 'Número do processo é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Busca nos sistemas dos tribunais
        result = CourtIntegrationService.search_process(process_number)
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def sync_with_court(self, request, pk=None):
        """
        Sincroniza processo existente com dados do tribunal
        """
        process = self.get_object()
        
        # Busca dados atualizados
        result = CourtIntegrationService.search_process(process.process_number)
        
        if not result.get('success'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        # Atualiza campos do processo
        data = result.get('data', {})
        
        if data.get('vara'):
            process.court = data['vara']
        
        if data.get('assunto'):
            process.description = data['assunto']
        
        if data.get('status'):
            process.status = data['status']
        
        if data.get('classe'):
            process.case_class = data['classe']
        
        if data.get('valor_causa'):
            try:
                process.actual_value = float(data['valor_causa'])
            except:
                pass
        
        # Extrai nomes das partes
        partes = data.get('partes', {})
        opposing = []
        if partes.get('reus'):
            opposing.extend(partes['reus'])
        if partes.get('outros'):
            opposing.extend(partes['outros'])
        
        if opposing:
            process.opposing_parties = ', '.join(opposing)
        
        process.last_sync_date = datetime.now()
        process.save()
        
        return Response({
            'message': 'Processo sincronizado com sucesso',
            'process': LegalProcessSerializer(process).data,
            'sync_data': result
        })
    
    @action(detail=False, methods=['get'])
    def lawyer_fees_report(self, request):
        """
        Relatório de honorários dos advogados
        """
        lawyer_id = request.query_params.get('lawyer_id')
        
        queryset = LegalProcess.objects.all()
        if lawyer_id:
            queryset = queryset.filter(lawyer_id=lawyer_id)
        
        report = []
        for process in queryset:
            if process.lawyer:
                total_fee = process.calculate_lawyer_fee()
                balance = process.get_lawyer_fee_balance()
                
                if total_fee > 0:
                    report.append({
                        'process_number': process.process_number,
                        'process_title': process.title,
                        'lawyer_name': process.lawyer.name,
                        'lawyer_oab': f"{process.lawyer.oab_number}/{process.lawyer.oab_state}",
                        'total_fee': str(total_fee),
                        'paid_fee': str(process.lawyer_fee_paid),
                        'balance': str(balance),
                        'status': process.status,
                    })
        
        # Agrupa por advogado
        summary = {}
        for item in report:
            lawyer = item['lawyer_name']
            if lawyer not in summary:
                summary[lawyer] = {
                    'lawyer_name': lawyer,
                    'lawyer_oab': item['lawyer_oab'],
                    'total_processes': 0,
                    'total_fees': 0,
                    'total_paid': 0,
                    'total_balance': 0
                }
            
            summary[lawyer]['total_processes'] += 1
            summary[lawyer]['total_fees'] += float(item['total_fee'])
            summary[lawyer]['total_paid'] += float(item['paid_fee'])
            summary[lawyer]['total_balance'] += float(item['balance'])
        
        return Response({
            'details': report,
            'summary': list(summary.values())
        })


class HearingViewSet(viewsets.ModelViewSet):
    queryset = Hearing.objects.all()
    serializer_class = HearingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Hearing.objects.all()
        
        status_param = self.request.query_params.get('status', None)
        process_id = self.request.query_params.get('process_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if process_id:
            queryset = queryset.filter(process_id=process_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.select_related('process').order_by('date')
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Próximas audiências (próximos 30 dias)"""
        today = datetime.now().date()
        end_date = today + timedelta(days=30)
        
        hearings = Hearing.objects.filter(
            date__date__gte=today,
            date__date__lte=end_date,
            status='scheduled'
        ).select_related('process').order_by('date')
        
        return Response(HearingSerializer(hearings, many=True).data)


class LegalContractViewSet(viewsets.ModelViewSet):
    queryset = LegalContract.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LegalContractListSerializer
        return LegalContractSerializer
    
    def get_queryset(self):
        queryset = LegalContract.objects.all()
        
        contract_type = self.request.query_params.get('contract_type', None)
        status_param = self.request.query_params.get('status', None)
        client_id = self.request.query_params.get('client_id', None)
        search = self.request.query_params.get('search', None)
        
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(title__icontains=search) |
                Q(counterpart__icontains=search)
            )
        
        return queryset.select_related('client', 'created_by').order_by('-start_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Alterar status do contrato"""
        contract = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Campo status é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract.status = new_status
        contract.save()
        
        return Response({
            'message': 'Status atualizado com sucesso',
            'contract': LegalContractSerializer(contract).data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Contratos expirando em breve (próximos 30 dias)"""
        today = datetime.now().date()
        end_date = today + timedelta(days=30)
        
        contracts = LegalContract.objects.filter(
            end_date__gte=today,
            end_date__lte=end_date,
            status='active'
        ).select_related('client').order_by('end_date')
        
        return Response(LegalContractListSerializer(contracts, many=True).data)


class LegalDeadlineViewSet(viewsets.ModelViewSet):
    queryset = LegalDeadline.objects.all()
    serializer_class = LegalDeadlineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = LegalDeadline.objects.all()
        
        status_param = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        process_id = self.request.query_params.get('process_id', None)
        responsible_id = self.request.query_params.get('responsible_id', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if priority:
            queryset = queryset.filter(priority=priority)
        if process_id:
            queryset = queryset.filter(process_id=process_id)
        if responsible_id:
            queryset = queryset.filter(responsible_id=responsible_id)
        
        return queryset.select_related('process', 'responsible').order_by('due_date')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar prazo como concluído"""
        deadline = self.get_object()
        
        deadline.status = 'completed'
        deadline.completion_date = datetime.now().date()
        deadline.save()
        
        return Response({
            'message': 'Prazo marcado como concluído',
            'deadline': LegalDeadlineSerializer(deadline).data
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Prazos atrasados"""
        today = datetime.now().date()
        
        deadlines = LegalDeadline.objects.filter(
            due_date__lt=today,
            status='pending'
        ).select_related('process', 'responsible').order_by('due_date')
        
        # Atualizar status para atrasado
        deadlines.update(status='overdue')
        
        return Response(LegalDeadlineSerializer(deadlines, many=True).data)
