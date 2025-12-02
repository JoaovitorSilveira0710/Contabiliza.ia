from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import RedirectView, TemplateView
from rest_framework.routers import DefaultRouter
from clients.views import ClientViewSet, FarmViewSet, cnpj_lookup
from invoices.views import InvoiceViewSet, InvoiceItemViewSet
from financial.views import (
    FinancialCategoryViewSet, BankAccountViewSet, FinancialTransactionViewSet,
    AccountsPayableViewSet, AccountsReceivableViewSet, CashFlowViewSet
)
from legal.views import (
    LawyerViewSet, LegalProcessViewSet, HearingViewSet,
    LegalContractViewSet, LegalDeadlineViewSet
)
from stock.views import (
    ProductCategoryViewSet, SupplierViewSet, WarehouseViewSet,
    ProductViewSet, StockMovementViewSet, StockCountViewSet, StockCountItemViewSet
)
from dashboard import views as dashboard_views
from core import auth_views
import os

# Router para ViewSets
router = DefaultRouter()
# Core
# (removido) users ViewSet não definido
# Clients
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'farms', FarmViewSet, basename='farm')
# (removido) client-contacts ViewSet não disponível
# Invoices
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'invoice-items', InvoiceItemViewSet, basename='invoice-item')
# Financial
router.register(r'financial-categories', FinancialCategoryViewSet, basename='financial-category')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'financial-transactions', FinancialTransactionViewSet, basename='financial-transaction')
router.register(r'accounts-payable', AccountsPayableViewSet, basename='accounts-payable')
router.register(r'accounts-receivable', AccountsReceivableViewSet, basename='accounts-receivable')
router.register(r'cash-flow', CashFlowViewSet, basename='cash-flow')
# Legal
router.register(r'lawyers', LawyerViewSet, basename='lawyer')
router.register(r'legal-processes', LegalProcessViewSet, basename='legal-process')
router.register(r'hearings', HearingViewSet, basename='hearing')
router.register(r'legal-contracts', LegalContractViewSet, basename='legal-contract')
router.register(r'legal-deadlines', LegalDeadlineViewSet, basename='legal-deadline')
# Stock
router.register(r'product-categories', ProductCategoryViewSet, basename='product-category')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')
router.register(r'stock-counts', StockCountViewSet, basename='stock-count')
router.register(r'stock-count-items', StockCountItemViewSet, basename='stock-count-item')

urlpatterns = [
    # Redirecionar root para index.html
    path('', RedirectView.as_view(url='/index.html', permanent=False)),
    # Favicon: redireciona /favicon.ico para um ícone estático
    path('favicon.ico', RedirectView.as_view(url='/icon.svg', permanent=False)),
    # Rotas DTL (validação inicial)
    path('tmpl/index', TemplateView.as_view(template_name='index.html'), name='tmpl-index'),
    path('tmpl/login', TemplateView.as_view(template_name='login.html'), name='tmpl-login'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Auth endpoints (with and without trailing slash)
    path('api/auth/login/', auth_views.login, name='api-login'),
    path('api/auth/login', auth_views.login, name='api-login-no-slash'),
    path('api/auth/logout/', auth_views.logout, name='api-logout'),
    path('api/auth/logout', auth_views.logout, name='api-logout-no-slash'),
    path('api/auth/check/', auth_views.check_auth, name='api-check-auth'),
    path('api/auth/check', auth_views.check_auth, name='api-check-auth-no-slash'),
    
    # API Router
    path('api/', include(router.urls)),

    # Utils
    path('api/utils/cnpj/<str:cnpj>/', cnpj_lookup, name='utils-cnpj-lookup'),
    
    # Dashboard endpoints
    path('api/dashboard/overview/', dashboard_views.dashboard_overview, name='dashboard-overview'),
    path('api/dashboard/revenue-chart/', dashboard_views.revenue_chart, name='revenue-chart'),
    path('api/dashboard/invoices-by-status/', dashboard_views.invoices_by_status, name='invoices-by-status'),
    path('api/dashboard/invoices-by-type/', dashboard_views.invoices_by_type, name='invoices-by-type'),
    path('api/dashboard/recent-activities/', dashboard_views.recent_activities, name='recent-activities'),
    path('api/dashboard/taxes-summary/', dashboard_views.taxes_summary, name='taxes-summary'),
    path('api/dashboard/weekly-performance/', dashboard_views.weekly_performance, name='weekly-performance'),
    
    # Auth
    path('api-auth/', include('rest_framework.urls')),
]

# Servir arquivos de media e frontend em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Servir arquivos do frontend
    frontend_path = settings.BASE_DIR.parent / 'frontend'
    urlpatterns += [
        re_path(r'^(?P<path>.*)$', serve, {
            'document_root': frontend_path,
        }),
    ]
