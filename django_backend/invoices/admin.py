from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('code', 'description', 'quantity', 'unit_value', 'total_value')
    readonly_fields = ('total_value',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'series', 'invoice_type', 'client', 'total_value', 'status', 'issue_date')
    list_filter = ('status', 'invoice_type', 'issue_date', 'created_at')
    search_fields = ('number', 'series', 'client__name', 'access_key')
    readonly_fields = ('access_key', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Identificação', {
            'fields': ('number', 'series', 'invoice_type', 'access_key', 'status')
        }),
        ('Partes', {
            'fields': ('client', 'issuer_name', 'issuer_tax_id')
        }),
        ('Datas', {
            'fields': ('issue_date', 'due_date', 'authorization_date')
        }),
        ('Valores', {
            'fields': ('total_products', 'total_services', 'discount', 'shipping', 'insurance', 'other_expenses', 'total_value')
        }),
        ('Impostos', {
            'fields': ('icms_base', 'icms_value', 'ipi_value', 'pis_value', 'cofins_value', 'iss_value')
        }),
        ('Arquivos', {
            'fields': ('xml_file', 'pdf_file')
        }),
        ('Informações Adicionais', {
            'fields': ('notes', 'additional_info')
        }),
        ('Metadata', {
            'fields': ('created_by', 'protocol', 'created_at', 'updated_at')
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'invoice', 'quantity', 'unit_value', 'total_value')
    list_filter = ('item_type', 'created_at')
    search_fields = ('code', 'description', 'invoice__number')
