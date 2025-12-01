from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, F
from .models import (
    ProductCategory, Supplier, Warehouse, Product,
    StockMovement, StockCount, StockCountItem
)
from .serializers import (
    ProductCategorySerializer, SupplierSerializer, WarehouseSerializer,
    ProductSerializer, ProductListSerializer, StockMovementSerializer,
    StockCountSerializer, StockCountListSerializer, StockCountItemSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Supplier.objects.filter(is_active=True)
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(trade_name__icontains=search) |
                Q(tax_id__icontains=search)
            )
        
        return queryset.order_by('name')


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        category_id = self.request.query_params.get('category_id', None)
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        low_stock = self.request.query_params.get('low_stock', None)
        search = self.request.query_params.get('search', None)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if low_stock == 'true':
            queryset = queryset.filter(current_stock__lte=F('minimum_stock'))
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        return queryset.select_related('category', 'default_supplier', 'warehouse').order_by('name')
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Produtos com estoque baixo"""
        products = Product.objects.filter(current_stock__lte=F('minimum_stock'), is_active=True)
        return Response(ProductListSerializer(products, many=True).data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de produtos"""
        total = Product.objects.filter(is_active=True).count()
        low_stock_count = Product.objects.filter(current_stock__lte=F('minimum_stock'), is_active=True).count()
        total_value = Product.objects.filter(is_active=True).aggregate(
            total=Sum(F('current_stock') * F('cost_price'))
        )['total'] or 0
        
        return Response({
            'total_products': total,
            'low_stock_count': low_stock_count,
            'total_stock_value': str(total_value)
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockMovement.objects.all()
        
        movement_type = self.request.query_params.get('movement_type', None)
        product_id = self.request.query_params.get('product_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.select_related('product', 'supplier', 'created_by').order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StockCountViewSet(viewsets.ModelViewSet):
    queryset = StockCount.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StockCountListSerializer
        return StockCountSerializer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Finalizar contagem"""
        stock_count = self.get_object()
        
        if stock_count.status != 'in_progress':
            return Response({'error': 'Contagem deve estar em andamento'}, status=status.HTTP_400_BAD_REQUEST)
        
        stock_count.status = 'completed'
        stock_count.save()
        
        return Response({'message': 'Contagem finalizada com sucesso'})


class StockCountItemViewSet(viewsets.ModelViewSet):
    queryset = StockCountItem.objects.all()
    serializer_class = StockCountItemSerializer
    permission_classes = [IsAuthenticated]
