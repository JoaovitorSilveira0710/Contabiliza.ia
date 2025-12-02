from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from clients.models import Client


class Command(BaseCommand):
    help = "Seed the database with sample PF and PJ clients with complete fields"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=6,
            help="Total number of clients to create (mix of PF/PJ)",
        )
        parser.add_argument(
            "--created-by-email",
            type=str,
            default=None,
            help="Email of user to set as created_by (optional)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        created_by_email = options["created_by_email"]
        created_by = None

        if created_by_email:
            User = get_user_model()
            try:
                created_by = User.objects.get(email=created_by_email)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"User with email {created_by_email} not found. Proceeding without created_by."))

        pf_samples = [
            {
                "person_type": "PF",
                "name": "Maria da Silva",
                "trade_name": None,
                "tax_id": "12345678901",  # CPF 11 dígitos
                "state_registration": None,
                "municipal_registration": None,
                "email": "maria.silva@example.com",
                "phone": "11987654321",
                "mobile": "11912345678",
                "zip_code": "01001000",
                "street": "Praça da Sé",
                "number": "100",
                "complement": "Apto 12",
                "neighborhood": "Sé",
                "city": "São Paulo",
                "state": "SP",
                "activity": "Consultoria autônoma",
                "status": "active",
                "tax_regime": "Pessoa Física",
                "payment_terms": 30,
                "credit_limit": 0,
                "notes": "Preferência por contato via e-mail",
            },
            {
                "person_type": "PF",
                "name": "João Pereira",
                "trade_name": None,
                "tax_id": "98765432100",
                "state_registration": None,
                "municipal_registration": None,
                "email": "joao.pereira@example.com",
                "phone": "21999887766",
                "mobile": "21988776655",
                "zip_code": "20040002",
                "street": "Rua da Assembléia",
                "number": "200",
                "complement": "Sala 305",
                "neighborhood": "Centro",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "activity": "Designer freelancer",
                "status": "active",
                "tax_regime": "Pessoa Física",
                "payment_terms": 15,
                "credit_limit": 0,
                "notes": "Atende preferencialmente em horário comercial",
            },
        ]

        pj_samples = [
            {
                "person_type": "PJ",
                "name": "Tech Brasil Soluções LTDA",
                "trade_name": "TechBrasil",
                "tax_id": "12345678000199",  # CNPJ 14 dígitos
                "state_registration": "ISENTO",
                "municipal_registration": "1234567",
                "email": "contato@techbrasil.com.br",
                "phone": "1133221100",
                "mobile": "11999887766",
                "zip_code": "04547005",
                "street": "Av. Brigadeiro Faria Lima",
                "number": "1500",
                "complement": "Conjunto 1203",
                "neighborhood": "Itaim Bibi",
                "city": "São Paulo",
                "state": "SP",
                "activity": "Desenvolvimento de software",
                "status": "active",
                "tax_regime": "Lucro Presumido",
                "payment_terms": 30,
                "credit_limit": 50000,
                "notes": "Cliente estratégico, condições negociadas",
            },
            {
                "person_type": "PJ",
                "name": "Comercial Norte Importações EIRELI",
                "trade_name": "Comercial Norte",
                "tax_id": "20987654000155",
                "state_registration": "123456789",
                "municipal_registration": "7654321",
                "email": "financeiro@comercialnorte.com",
                "phone": "3133557799",
                "mobile": "31988776655",
                "zip_code": "30140071",
                "street": "Av. Getúlio Vargas",
                "number": "900",
                "complement": "Loja 2",
                "neighborhood": "Funcionários",
                "city": "Belo Horizonte",
                "state": "MG",
                "activity": "Comércio atacadista",
                "status": "active",
                "tax_regime": "Simples Nacional",
                "payment_terms": 45,
                "credit_limit": 20000,
                "notes": "Solicitou aumento de limite",
            },
            {
                "person_type": "PJ",
                "name": "Alfa Serviços Integrados S/A",
                "trade_name": "Alfa Serviços",
                "tax_id": "11445566000122",
                "state_registration": "99887766",
                "municipal_registration": "55443322",
                "email": "contato@alfaservicos.com",
                "phone": "4133665522",
                "mobile": "41999887766",
                "zip_code": "80010020",
                "street": "Rua XV de Novembro",
                "number": "50",
                "complement": "Andar 7",
                "neighborhood": "Centro",
                "city": "Curitiba",
                "state": "PR",
                "activity": "Serviços gerais e facilities",
                "status": "inactive",
                "tax_regime": "Lucro Real",
                "payment_terms": 60,
                "credit_limit": 100000,
                "notes": "Empresa em reestruturação",
            },
            {
                "person_type": "PJ",
                "name": "Bahia Produtos Agrícolas LTDA",
                "trade_name": "Bahia Agro",
                "tax_id": "55667788000133",
                "state_registration": "11223344",
                "municipal_registration": "44332211",
                "email": "contato@bahiaagro.com.br",
                "phone": "7133124455",
                "mobile": "71999887766",
                "zip_code": "40020000",
                "street": "Rua Chile",
                "number": "10",
                "complement": "Sala 2",
                "neighborhood": "Centro",
                "city": "Salvador",
                "state": "BA",
                "activity": "Comércio de insumos agrícolas",
                "status": "active",
                "tax_regime": "Simples Nacional",
                "payment_terms": 30,
                "credit_limit": 15000,
                "notes": "Preferência por boletos quinzenais",
            },
        ]

        # Build dataset according to requested count
        dataset = []
        # Ensure at least 2 PF and 3 PJ if count allows
        base = pf_samples + pj_samples
        while len(dataset) < count:
            dataset.extend(base)
        dataset = dataset[:count]

        created = 0
        for data in dataset:
            # Enforce unique tax_id: skip if exists
            if Client.objects.filter(tax_id=data["tax_id"]).exists():
                self.stdout.write(self.style.WARNING(f"Client with tax_id {data['tax_id']} already exists, skipping."))
                continue

            obj = Client(**data)
            obj.created_by = created_by
            obj.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} clients."))