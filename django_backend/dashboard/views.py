from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta
from clients.models import Client
from invoices.models import Invoice
from decimal import Decimal


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Main dashboard with system overview"""
    
    # Period
    today = datetime.now()
    first_day_month = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)
    
    # Clients
    clients_stats = {
        'total': Client.objects.count(),
        'active': Client.objects.filter(status='active').count(),
        'new_this_month': Client.objects.filter(created_at__gte=first_day_month).count(),
        'pessoa_fisica': Client.objects.filter(person_type='PF').count(),
        'pessoa_juridica': Client.objects.filter(person_type='PJ').count(),
    }
    
    # Invoices
    invoices_stats = {
        'total': Invoice.objects.count(),
        'authorized': Invoice.objects.filter(status='authorized').count(),
        'pending': Invoice.objects.filter(status='pending').count(),
        'cancelled': Invoice.objects.filter(status='cancelled').count(),
        'this_month': Invoice.objects.filter(issue_date__gte=first_day_month).count(),
    }
    
    # Financial values
    financial_stats = Invoice.objects.filter(status='authorized').aggregate(
        total_value=Sum('total_value'),
        total_taxes=Sum('icms_value') + Sum('ipi_value') + Sum('pis_value') + Sum('cofins_value'),
        avg_value=Avg('total_value')
    )
    
    # Monthly revenue
    month_revenue = Invoice.objects.filter(
        status='authorized',
        issue_date__gte=first_day_month
    ).aggregate(total=Sum('total_value'))['total'] or Decimal('0.00')
    
    # Revenue from last 30 days
    recent_revenue = Invoice.objects.filter(
        status='authorized',
        issue_date__gte=thirty_days_ago
    ).aggregate(total=Sum('total_value'))['total'] or Decimal('0.00')
    
    # Top 5 clients (by invoice value)
    top_clients = Client.objects.annotate(
        total_invoiced=Sum('invoices__total_value', filter=Q(invoices__status='authorized'))
    ).order_by('-total_invoiced')[:5].values('id', 'name', 'tax_id', 'total_invoiced')
    
    return Response({
        'clients': clients_stats,
        'invoices': invoices_stats,
        'financial': {
            'total_value': str(financial_stats['total_value'] or 0),
            'total_taxes': str(financial_stats['total_taxes'] or 0),
            'avg_value': str(financial_stats['avg_value'] or 0),
            'month_revenue': str(month_revenue),
            'recent_revenue': str(recent_revenue),
        },
        'top_clients': list(top_clients),
        'last_update': datetime.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_chart(request):
    """Data for monthly revenue chart"""
    
    # Last 12 months
    twelve_months_ago = datetime.now() - timedelta(days=365)
    
    monthly_revenue = Invoice.objects.filter(
        status='authorized',
        issue_date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('issue_date')
    ).values('month').annotate(
        total=Sum('total_value'),
        count=Count('id')
    ).order_by('month')
    
    return Response({
        'labels': [item['month'].strftime('%m/%Y') for item in monthly_revenue],
        'data': [float(item['total']) for item in monthly_revenue],
        'counts': [item['count'] for item in monthly_revenue]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoices_by_status(request):
    """Distribuição de notas por status"""
    
    by_status = Invoice.objects.values('status').annotate(
        count=Count('id'),
        total=Sum('total_value')
    )
    
    status_labels = dict(Invoice.STATUS_CHOICES)
    
    return Response({
        'labels': [status_labels.get(item['status'], item['status']) for item in by_status],
        'data': [item['count'] for item in by_status],
        'values': [float(item['total'] or 0) for item in by_status]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoices_by_type(request):
    """Distribuição de notas por tipo"""
    
    by_type = Invoice.objects.values('invoice_type').annotate(
        count=Count('id'),
        total=Sum('total_value')
    )
    
    type_labels = dict(Invoice.INVOICE_TYPE_CHOICES)
    
    return Response({
        'labels': [type_labels.get(item['invoice_type'], item['invoice_type']) for item in by_type],
        'data': [item['count'] for item in by_type],
        'values': [float(item['total'] or 0) for item in by_type]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activities(request):
    """Recent system activities"""
    
    # Last 10 invoices
    recent_invoices = Invoice.objects.select_related('client', 'created_by').order_by('-created_at')[:10].values(
        'id', 'number', 'series', 'status', 'total_value', 'created_at',
        'client__name', 'created_by__first_name', 'created_by__last_name'
    )
    
    # Last 10 registered clients
    recent_clients = Client.objects.select_related('created_by').order_by('-created_at')[:10].values(
        'id', 'name', 'tax_id', 'status', 'created_at',
        'created_by__first_name', 'created_by__last_name'
    )
    
    return Response({
        'invoices': list(recent_invoices),
        'clients': list(recent_clients)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def taxes_summary(request):
    """Tax summary"""
    
    # Period
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    queryset = Invoice.objects.filter(status='authorized')
    
    if start_date:
        queryset = queryset.filter(issue_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(issue_date__lte=end_date)
    
    taxes = queryset.aggregate(
        icms=Sum('icms_value'),
        ipi=Sum('ipi_value'),
        pis=Sum('pis_value'),
        cofins=Sum('cofins_value'),
        iss=Sum('iss_value')
    )
    
    total_taxes = sum(Decimal(str(v or 0)) for v in taxes.values())
    
    return Response({
        'icms': str(taxes['icms'] or 0),
        'ipi': str(taxes['ipi'] or 0),
        'pis': str(taxes['pis'] or 0),
        'cofins': str(taxes['cofins'] or 0),
        'iss': str(taxes['iss'] or 0),
        'total': str(total_taxes)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_performance(request):
    """Weekly performance"""
    
    # Last 8 weeks
    eight_weeks_ago = datetime.now() - timedelta(weeks=8)
    
    weekly_data = Invoice.objects.filter(
        status='authorized',
        issue_date__gte=eight_weeks_ago
    ).annotate(
        week=TruncWeek('issue_date')
    ).values('week').annotate(
        total=Sum('total_value'),
        count=Count('id')
    ).order_by('week')
    
    return Response({
        'labels': [item['week'].strftime('%d/%m') for item in weekly_data],
        'revenue': [float(item['total']) for item in weekly_data],
        'invoices': [item['count'] for item in weekly_data]
    })
