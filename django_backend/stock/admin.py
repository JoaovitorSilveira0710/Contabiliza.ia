from django.contrib import admin
from .models import ProductCategory, Supplier, Warehouse, Product, StockMovement, StockCount, StockCountItem


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'email', 'phone', 'city', 'state', 'is_active')
    list_filter = ('is_active', 'state')
    search_fields = ('name', 'trade_name', 'tax_id')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'state', 'manager', 'is_active')
    list_filter = ('is_active', 'state')
    search_fields = ('code', 'name', 'city')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'current_stock', 'minimum_stock', 'cost_price', 'sale_price', 'is_active')
    list_filter = ('is_active', 'category', 'warehouse')
    search_fields = ('code', 'name', 'barcode')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'date', 'created_by')
    list_filter = ('movement_type', 'date')
    search_fields = ('product__name', 'document_number')
    readonly_fields = ('total_cost', 'created_at')


class StockCountItemInline(admin.TabularInline):
    model = StockCountItem
    extra = 0


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'warehouse', 'count_date', 'status')
    list_filter = ('status', 'warehouse', 'count_date')
    search_fields = ('code', 'description')
    inlines = [StockCountItemInline]
