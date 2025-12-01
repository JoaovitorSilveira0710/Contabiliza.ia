from rest_framework import serializers
from .models import (
    ProductCategory, Supplier, Warehouse, Product,
    StockMovement, StockCount, StockCountItem
)


class ProductCategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'is_active', 'products_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_products_count(self, obj):
        return obj.products.count()


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'trade_name', 'tax_id', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'contact_person',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WarehouseSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'code', 'address', 'city', 'state', 'zip_code',
            'manager', 'phone', 'products_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='default_supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'description', 'category', 'category_name',
            'unit', 'current_stock', 'minimum_stock', 'maximum_stock',
            'cost_price', 'sale_price', 'default_supplier', 'supplier_name',
            'warehouse', 'warehouse_name', 'location', 'barcode', 'ncm',
            'is_low_stock', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 'supplier_name', 'warehouse_name', 'is_low_stock']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'category_name', 'current_stock', 'minimum_stock', 'is_low_stock', 'cost_price', 'sale_price']


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'quantity',
            'unit_cost', 'total_cost', 'source_warehouse', 'destination_warehouse',
            'supplier', 'supplier_name', 'document_number', 'date', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'total_cost', 'created_at', 'product_name', 'supplier_name', 'created_by_name']


class StockCountItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    
    class Meta:
        model = StockCountItem
        fields = [
            'id', 'product', 'product_name', 'product_code',
            'system_quantity', 'counted_quantity', 'difference', 'notes'
        ]
        read_only_fields = ['id', 'difference']


class StockCountSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    responsible_name = serializers.CharField(source='responsible.get_full_name', read_only=True)
    items = StockCountItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StockCount
        fields = [
            'id', 'code', 'description', 'warehouse', 'warehouse_name',
            'count_date', 'status', 'notes', 'responsible', 'responsible_name',
            'items', 'items_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'warehouse_name', 'responsible_name']
    
    def get_items_count(self, obj):
        return obj.items.count()


class StockCountListSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = StockCount
        fields = ['id', 'code', 'description', 'warehouse_name', 'count_date', 'status']
