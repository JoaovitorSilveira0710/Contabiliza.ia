"""
URL configuration for contabiliza_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from clients.views import (
    ClientViewSet,
    ContractViewSet,
    ContractedServiceViewSet,
    DashboardMetricViewSet,
    AuditViewSet,
)
from invoices.views import InvoiceViewSet
from documents.views import DocumentViewSet
from core.views import UserViewSet, RoleViewSet
from financial.views import ProductViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'contracted-services', ContractedServiceViewSet, basename='contracted-service')
router.register(r'dashboard-metrics', DashboardMetricViewSet, basename='dashboard-metric')
router.register(r'audits', AuditViewSet, basename='audit')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
