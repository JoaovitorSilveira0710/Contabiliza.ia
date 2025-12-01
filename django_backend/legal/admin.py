from django.contrib import admin
from .models import Lawyer, LegalProcess, Hearing, LegalContract, LegalDeadline


@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'oab_number', 'oab_state', 'email', 'phone', 'is_active')
    list_filter = ('oab_state', 'is_active')
    search_fields = ('name', 'oab_number', 'email')


class HearingInline(admin.TabularInline):
    model = Hearing
    extra = 0
    fields = ('hearing_type', 'date', 'location', 'status')


class LegalDeadlineInline(admin.TabularInline):
    model = LegalDeadline
    extra = 0
    fields = ('title', 'due_date', 'priority', 'status')


@admin.register(LegalProcess)
class LegalProcessAdmin(admin.ModelAdmin):
    list_display = ('process_number', 'title', 'process_type', 'client', 'lawyer', 'status', 'priority', 'start_date')
    list_filter = ('process_type', 'status', 'priority', 'start_date')
    search_fields = ('process_number', 'title', 'client__name')
    inlines = [HearingInline, LegalDeadlineInline]
    date_hierarchy = 'start_date'


@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ('process', 'hearing_type', 'date', 'location', 'status')
    list_filter = ('hearing_type', 'status', 'date')
    search_fields = ('process__process_number', 'location')
    date_hierarchy = 'date'


@admin.register(LegalContract)
class LegalContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'contract_type', 'client', 'status', 'start_date', 'end_date', 'contract_value')
    list_filter = ('contract_type', 'status', 'start_date')
    search_fields = ('contract_number', 'title', 'client__name', 'counterpart')
    date_hierarchy = 'start_date'


@admin.register(LegalDeadline)
class LegalDeadlineAdmin(admin.ModelAdmin):
    list_display = ('title', 'process', 'due_date', 'priority', 'status', 'responsible')
    list_filter = ('priority', 'status', 'due_date')
    search_fields = ('title', 'process__process_number')
    date_hierarchy = 'due_date'
