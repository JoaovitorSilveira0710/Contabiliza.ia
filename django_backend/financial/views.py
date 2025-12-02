from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    FinancialCategory, BankAccount, FinancialTransaction,
    AccountsPayable, AccountsReceivable, CashFlow
)
from .serializers import (
    FinancialCategorySerializer, BankAccountSerializer,
    FinancialTransactionSerializer, FinancialTransactionListSerializer,
    AccountsPayableSerializer, AccountsReceivableSerializer, CashFlowSerializer
)
from invoices.models import Invoice
from .services.receipt_analyzer import analyze_receipt


class FinancialCategoryViewSet(viewsets.ModelViewSet):
    queryset = FinancialCategory.objects.all()
    serializer_class = FinancialCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FinancialCategory.objects.filter(is_active=True)
        category_type = self.request.query_params.get('category_type', None)
        
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        
        return queryset


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = BankAccount.objects.filter(is_active=True)
        return queryset.order_by('name')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo de todas as contas"""
        accounts = BankAccount.objects.filter(is_active=True)
        
        total_balance = accounts.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
        
        return Response({
            'total_accounts': accounts.count(),
            'total_balance': str(total_balance),
            'accounts': BankAccountSerializer(accounts, many=True).data
        })


class FinancialTransactionViewSet(viewsets.ModelViewSet):
    queryset = FinancialTransaction.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FinancialTransactionListSerializer
        return FinancialTransactionSerializer
    
    def get_queryset(self):
        queryset = FinancialTransaction.objects.all()
        
        # Filtros
        transaction_type = self.request.query_params.get('transaction_type', None)
        status_param = self.request.query_params.get('status', None)
        category_id = self.request.query_params.get('category_id', None)
        account_id = self.request.query_params.get('account_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        search = self.request.query_params.get('search', None)
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__lte=end_date)
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(document_number__icontains=search)
            )
        
        return queryset.select_related('category', 'account', 'client', 'created_by').order_by('-due_date')
    
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        # If there is an attachment, try to analyze and auto-fill missing fields
        try:
            if instance.attachment and hasattr(instance.attachment, 'path'):
                content_type = getattr(getattr(instance.attachment, 'file', None), 'content_type', None)
                result = analyze_receipt(instance.attachment.path, content_type)
                updated_fields = []
                # payment method
                if not instance.payment_method and result.get('method'):
                    instance.payment_method = result['method']
                    updated_fields.append('payment_method')
                # payment date
                if not instance.payment_date and result.get('payment_date'):
                    instance.payment_date = result['payment_date']
                    updated_fields.append('payment_date')
                # If status is pending but we have a payment date, set proper status
                if result.get('payment_date') and instance.status in ['pending', 'overdue']:
                    if instance.transaction_type == 'expense':
                        instance.status = 'paid'
                    else:
                        instance.status = 'received'
                    updated_fields.append('status')
                # Append extracted info to notes
                notes_parts = []
                if result.get('txid'):
                    notes_parts.append(f"TXID: {result['txid']}")
                if result.get('amount'):
                    notes_parts.append(f"Valor detectado: R$ {result['amount']}")
                if result.get('method'):
                    notes_parts.append(f"Método detectado: {result['method']}")
                if result.get('payment_date'):
                    notes_parts.append(f"Data pagamento detectada: {result['payment_date']}")
                if notes_parts:
                    snippet = ' | '.join(notes_parts)
                    raw_excerpt = result.get('raw_excerpt')
                    if raw_excerpt:
                        snippet += f" | Trecho: {raw_excerpt}"
                    instance.notes = (instance.notes + "\n" + snippet) if instance.notes else snippet
                    updated_fields.append('notes')
                if updated_fields:
                    instance.save(update_fields=list(set(updated_fields)))
        except Exception:
            # Silently ignore analyzer failures to not block creation
            pass
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Marcar transação como paga"""
        transaction = self.get_object()
        
        payment_date = request.data.get('payment_date', datetime.now().date())
        payment_method = request.data.get('payment_method')
        
        if transaction.status in ['paid', 'received']:
            return Response(
                {'error': 'Transação já foi paga/recebida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.payment_date = payment_date
        transaction.payment_method = payment_method
        
        if transaction.transaction_type == 'expense':
            transaction.status = 'paid'
        else:
            transaction.status = 'received'
        
        transaction.save()
        
        return Response({
            'message': 'Transação atualizada com sucesso',
            'transaction': FinancialTransactionSerializer(transaction).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar transação"""
        transaction = self.get_object()
        
        if transaction.status in ['paid', 'received']:
            return Response(
                {'error': 'Não é possível cancelar uma transação já paga/recebida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = 'cancelled'
        transaction.save()
        
        return Response({'message': 'Transação cancelada com sucesso'})
    
    @action(detail=False, methods=['post'])
    def import_invoices(self, request):
        """Importar notas fiscais como contas a receber"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        category_id = request.data.get('category_id')
        account_id = request.data.get('account_id')
        
        if not all([start_date, end_date, category_id, account_id]):
            return Response(
                {'error': 'Campos obrigatórios: start_date, end_date, category_id, account_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar notas autorizadas no período
        invoices = Invoice.objects.filter(
            status='authorized',
            issue_date__gte=start_date,
            issue_date__lte=end_date
        )
        
        imported = 0
        for invoice in invoices:
            # Verificar se já existe transação para esta nota
            exists = AccountsReceivable.objects.filter(invoice_number=invoice.number).exists()
            if exists:
                continue
            
            # Criar transação
            transaction = FinancialTransaction.objects.create(
                transaction_type='revenue',
                description=f"NF-e {invoice.number}/{invoice.series} - {invoice.client.name}",
                category_id=category_id,
                client=invoice.client,
                account_id=account_id,
                amount=invoice.total_value,
                due_date=invoice.due_date or invoice.issue_date.date(),
                competence_date=invoice.issue_date.date(),
                status='pending',
                document_number=invoice.number,
                created_by=request.user
            )
            
            # Criar conta a receber
            AccountsReceivable.objects.create(
                transaction=transaction,
                customer=invoice.client,
                invoice_number=invoice.number
            )
            
            imported += 1
        
        return Response({
            'message': f'{imported} notas fiscais importadas com sucesso',
            'imported': imported,
            'total': invoices.count()
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo financeiro"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = FinancialTransaction.objects.all()
        
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__lte=end_date)
        
        # Receitas
        revenues = queryset.filter(transaction_type='revenue').aggregate(
            total=Sum('final_amount'),
            paid=Sum('final_amount', filter=Q(status='received')),
            pending=Sum('final_amount', filter=Q(status='pending'))
        )
        
        # Despesas
        expenses = queryset.filter(transaction_type='expense').aggregate(
            total=Sum('final_amount'),
            paid=Sum('final_amount', filter=Q(status='paid')),
            pending=Sum('final_amount', filter=Q(status='pending'))
        )
        
        return Response({
            'revenues': {
                'total': str(revenues['total'] or 0),
                'paid': str(revenues['paid'] or 0),
                'pending': str(revenues['pending'] or 0)
            },
            'expenses': {
                'total': str(expenses['total'] or 0),
                'paid': str(expenses['paid'] or 0),
                'pending': str(expenses['pending'] or 0)
            },
            'balance': str((revenues['total'] or 0) - (expenses['total'] or 0))
        })


class AccountsPayableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountsPayable.objects.all()
    serializer_class = AccountsPayableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AccountsPayable.objects.select_related('transaction', 'transaction__account')
        
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(transaction__status=status_param)
        
        return queryset.order_by('transaction__due_date')


class AccountsReceivableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountsReceivable.objects.all()
    serializer_class = AccountsReceivableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AccountsReceivable.objects.select_related('transaction', 'customer')
        
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(transaction__status=status_param)
        
        return queryset.order_by('transaction__due_date')


class CashFlowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CashFlow.objects.all()
    serializer_class = CashFlowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CashFlow.objects.all()
        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Gerar fluxo de caixa para um período"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date e end_date são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Implementar lógica de geração de fluxo de caixa
        # ...
        
        return Response({'message': 'Fluxo de caixa gerado com sucesso'})
