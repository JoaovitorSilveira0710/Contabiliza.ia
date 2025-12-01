from django.contrib import admin
from .models import Client, ClientContact


class ClientContactInline(admin.TabularInline):
    model = ClientContact
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'person_type', 'status', 'city', 'state', 'created_at')
    list_filter = ('status', 'person_type', 'state', 'created_at')
    search_fields = ('name', 'trade_name', 'tax_id', 'email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClientContactInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('person_type', 'name', 'trade_name', 'status')
        }),
        ('Documentos', {
            'fields': ('tax_id', 'state_registration', 'municipal_registration')
        }),
        ('Contato', {
            'fields': ('email', 'phone', 'mobile')
        }),
        ('Endereço', {
            'fields': ('zip_code', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')
        }),
        ('Informações Contábeis', {
            'fields': ('activity', 'tax_regime', 'payment_terms', 'credit_limit')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'position', 'email', 'phone', 'is_main')
    list_filter = ('is_main', 'created_at')
    search_fields = ('name', 'email', 'client__name')
