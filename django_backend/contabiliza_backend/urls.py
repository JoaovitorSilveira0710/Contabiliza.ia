from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from core.views import UserViewSet
from clients.views import ClientViewSet, ClientContactViewSet
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

# Router para ViewSets
router = DefaultRouter()
# Core
router.register(r'users', UserViewSet, basename='user')
# Clients
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'client-contacts', ClientContactViewSet, basename='client-contact')
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
    # Admin
    path('admin/', admin.site.urls),
    
    # API Router
    path('api/', include(router.urls)),
    
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

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
