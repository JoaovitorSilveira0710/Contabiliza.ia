from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from clients.models import Client
from django.contrib.auth import get_user_model
from financial.models import FinancialCategory, BankAccount, FinancialTransaction


class Command(BaseCommand):
    help = 'Cria categorias, conta bancária e lançamentos financeiros básicos com saldo positivo'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('Nenhum usuário encontrado para atribuir como created_by.'))
            return

        client = Client.objects.first()
        if not client:
            self.stdout.write(self.style.ERROR('Nenhum cliente encontrado. Crie clientes antes de semear finanças.'))
            return

        # Conta bancária
        account, _ = BankAccount.objects.get_or_create(
            name='Conta Principal',
            defaults={
                'account_type': 'checking',
                'bank_name': 'Banco Exemplo',
                'initial_balance': Decimal('500.00'),
                'current_balance': Decimal('500.00'),
            }
        )

        # Categorias
        cat_receita, _ = FinancialCategory.objects.get_or_create(
            name='Vendas',
            defaults={'category_type': 'revenue', 'color': '#16A34A'}
        )
        cat_servico, _ = FinancialCategory.objects.get_or_create(
            name='Serviços',
            defaults={'category_type': 'revenue', 'color': '#0EA5E9'}
        )
        cat_despesa, _ = FinancialCategory.objects.get_or_create(
            name='Despesas Operacionais',
            defaults={'category_type': 'expense', 'color': '#DC2626'}
        )

        today = timezone.localdate()

        created = 0

        def add_tx(t_type, desc, cat, amt, status, paid=True):
            nonlocal created
            tx = FinancialTransaction(
                transaction_type=t_type,
                description=desc,
                category=cat,
                client=client,
                account=account,
                amount=Decimal(amt),
                discount=Decimal('0.00'),
                interest=Decimal('0.00'),
                fine=Decimal('0.00'),
                due_date=today,
                competence_date=today,
                status=status,
                created_by=user,
            )
            # payment_date e payment_method se pago/recebido
            if paid:
                tx.payment_date = today
                tx.payment_method = 'pix'
            tx.save()
            created += 1
            return tx

        # Receitas (recebidas)
        add_tx('revenue', 'Recebimento de venda #1001', cat_receita, '1500.00', 'received')
        add_tx('revenue', 'Recebimento de serviço contrato A', cat_servico, '800.00', 'received')

        # Receita pendente
        add_tx('revenue', 'NF a receber #1002', cat_receita, '400.00', 'pending', paid=False)

        # Despesas (pagas)
        add_tx('expense', 'Energia elétrica', cat_despesa, '350.00', 'paid')
        add_tx('expense', 'Internet e telefonia', cat_despesa, '250.00', 'paid')

        # Despesa pendente
        add_tx('expense', 'Manutenção preventiva', cat_despesa, '180.00', 'pending', paid=False)

        self.stdout.write(self.style.SUCCESS(f'{created} lançamentos criados. Conta atualizada: R$ {account.current_balance:.2f}'))
