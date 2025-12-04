from django.db import models
from django.conf import settings


class ProductCategory(models.Model):
    """Categoria de Produto"""
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria de Produto'
        verbose_name_plural = 'Categorias de Produtos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Fornecedor"""
    name = models.CharField('Nome', max_length=200)
    trade_name = models.CharField('Nome Fantasia', max_length=200, blank=True)
    tax_id = models.CharField('CNPJ', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    address = models.CharField('Endereço', max_length=200, blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    state = models.CharField('Estado', max_length=2, blank=True)
    zip_code = models.CharField('CEP', max_length=10, blank=True)
    contact_person = models.CharField('Pessoa de Contato', max_length=100, blank=True)
    notes = models.TextField('Observações', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['name']

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """Depósito/Armazém"""
    name = models.CharField('Nome', max_length=100)
    code = models.CharField('Código', max_length=20, unique=True)
    address = models.CharField('Endereço', max_length=200)
    city = models.CharField('Cidade', max_length=100)
    state = models.CharField('Estado', max_length=2)
    zip_code = models.CharField('CEP', max_length=10, blank=True)
    manager = models.CharField('Gerente', max_length=100, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    """Produto"""
    UNIT_TYPES = [
        ('un', 'Unidade'),
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('m', 'Metro'),
        ('m2', 'Metro Quadrado'),
        ('m3', 'Metro Cúbico'),
        ('cx', 'Caixa'),
        ('pc', 'Peça'),
    ]
    
    code = models.CharField('Código', max_length=50, unique=True)
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='Categoria')
    unit = models.CharField('Unidade', max_length=10, choices=UNIT_TYPES, default='un')
    
    # Stock
    current_stock = models.DecimalField('Estoque Atual', max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField('Estoque Mínimo', max_digits=10, decimal_places=2, default=0)
    maximum_stock = models.DecimalField('Estoque Máximo', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Prices
    cost_price = models.DecimalField('Preço de Custo', max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2, default=0)
    
    # Default supplier
    default_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='Fornecedor Padrão')
    
    # Location
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='Depósito')
    location = models.CharField('Localização', max_length=50, blank=True, help_text='Ex: Corredor A, Prateleira 3')
    
    # Controle
    barcode = models.CharField('Código de Barras', max_length=50, blank=True)
    ncm = models.CharField('NCM', max_length=10, blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock


class StockMovement(models.Model):
    """Movimentação de Estoque"""
    MOVEMENT_TYPES = [
        ('entry', 'Entrada'),
        ('exit', 'Saída'),
        ('transfer', 'Transferência'),
        ('adjustment', 'Ajuste'),
        ('return', 'Devolução'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements', verbose_name='Produto')
    movement_type = models.CharField('Tipo', max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField('Quantidade', max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField('Custo Unitário', max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField('Custo Total', max_digits=15, decimal_places=2, null=True, blank=True)
    
    # For transfers
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_movements', verbose_name='Depósito Origem')
    destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_movements', verbose_name='Depósito Destino')
    
    # References
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements', verbose_name='Fornecedor')
    document_number = models.CharField('Número do Documento', max_length=50, blank=True)
    
    date = models.DateTimeField('Data')
    notes = models.TextField('Observações', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_movements', verbose_name='Criado por')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Atualizar estoque do produto
        if self.movement_type == 'entry':
            self.product.current_stock += self.quantity
        elif self.movement_type == 'exit':
            self.product.current_stock -= self.quantity
        
        # Calcular custo total
        if self.unit_cost and self.quantity:
            self.total_cost = self.unit_cost * self.quantity
        
        self.product.save()
        super().save(*args, **kwargs)


class StockCount(models.Model):
    """Contagem de Estoque / Inventário"""
    STATUS = [
        ('draft', 'Rascunho'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    code = models.CharField('Código', max_length=50, unique=True)
    description = models.CharField('Descrição', max_length=200)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_counts', verbose_name='Depósito')
    count_date = models.DateField('Data da Contagem')
    status = models.CharField('Status', max_length=20, choices=STATUS, default='draft')
    notes = models.TextField('Observações', blank=True)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_counts', verbose_name='Responsável')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Contagem de Estoque'
        verbose_name_plural = 'Contagens de Estoque'
        ordering = ['-count_date']

    def __str__(self):
        return f"{self.code} - {self.description}"


class StockCountItem(models.Model):
    """Item de Contagem de Estoque"""
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name='items', verbose_name='Contagem')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='count_items', verbose_name='Produto')
    system_quantity = models.DecimalField('Quantidade Sistema', max_digits=10, decimal_places=2)
    counted_quantity = models.DecimalField('Quantidade Contada', max_digits=10, decimal_places=2, null=True, blank=True)
    difference = models.DecimalField('Diferença', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Item de Contagem'
        verbose_name_plural = 'Itens de Contagem'
        unique_together = ['stock_count', 'product']

    def __str__(self):
        return f"{self.stock_count.code} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculate difference
        if self.counted_quantity is not None:
            self.difference = self.counted_quantity - self.system_quantity
        super().save(*args, **kwargs)
