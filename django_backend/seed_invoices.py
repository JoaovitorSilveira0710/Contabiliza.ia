import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliza_backend.settings')
django.setup()

from clients.models import Client
from invoices.models import Invoice, InvoiceItem


def seed_invoices():
    clients = list(Client.objects.all()[:5])
    if not clients:
        print('Nenhum cliente encontrado. Cadastre clientes antes de semear notas.')
        return

    base_issue = datetime.now() - timedelta(days=3)
    created = 0

    for idx, client in enumerate(clients, start=1):
        number = f"NF-{datetime.now().strftime('%Y%m%d')}-{idx:03d}"
        if Invoice.objects.filter(number=number).exists():
            print(f"Nota {number} já existe, pulando...")
            continue

        inv = Invoice(
            number=number,
            series='1',
            invoice_type='nfe',
            client=client,
            issuer_name='Contabiliza IA Ltda',
            issuer_tax_id='12.345.678/0001-90',
            issue_date=base_issue + timedelta(hours=idx),
            total_products=Decimal('1000.00') + Decimal(idx) * Decimal('250.00'),
            total_services=Decimal('0.00'),
            discount=Decimal('0.00'),
            shipping=Decimal('0.00'),
            insurance=Decimal('0.00'),
            other_expenses=Decimal('0.00'),
            icms_base=Decimal('0.00'),
            icms_value=Decimal('0.00'),
            ipi_value=Decimal('0.00'),
            pis_value=Decimal('0.00'),
            cofins_value=Decimal('0.00'),
            iss_value=Decimal('0.00'),
            total_value=Decimal('0.00'),  # calculado abaixo
            status='pending',
        )
        inv.calculate_total()
        # Alterna status: algumas autorizadas, outras pendentes
        if idx % 2 == 0:
            inv.status = 'authorized'
            inv.authorization_date = datetime.now()
        inv.save()

        # Adiciona um item simples
        item = InvoiceItem(
            invoice=inv,
            item_type='product',
            code=f"PROD-{idx:03d}",
            description='Produto de teste',
            ncm='12019000',
            cfop='5101',
            unit='un',
            quantity=Decimal('10.0000'),
            unit_value=Decimal('100.00'),
            discount=Decimal('0.00'),
        )
        item.save()

        created += 1
        print(f"Criada nota {inv.number} ({inv.status}) para cliente {client.name}")

    print(f"Concluído. Notas criadas: {created}")


if __name__ == '__main__':
    seed_invoices()
