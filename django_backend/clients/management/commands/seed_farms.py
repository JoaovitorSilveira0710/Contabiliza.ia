from django.core.management.base import BaseCommand
from django.db import transaction

from clients.models import Client


class Command(BaseCommand):
    help = "Seed sample farms by appending notes to PF clients to represent farm ownership"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=4,
            help="Number of farm entries to distribute across PF clients",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]

        pf_clients = list(Client.objects.filter(person_type="PF").order_by("name"))
        if not pf_clients:
            self.stdout.write(self.style.WARNING("No PF clients found to attach farms."))
            return

        # Sample farms spread across states; keep only one in PR
        farm_samples = [
            {
                "name": "Fazenda Santa Rita",
                "city": "Salvador",
                "state": "BA",
                "matricula": "BA-00123",
                "car": "BA-CAR-7788",
                "itr": "BA-ITR-5544",
                "ccir": "BA-CCIR-1122",
                "area": "150.0",
            },
            {
                "name": "Fazenda São José",
                "city": "Belo Horizonte",
                "state": "MG",
                "matricula": "MG-00999",
                "car": "MG-CAR-2233",
                "itr": "MG-ITR-3344",
                "ccir": "MG-CCIR-8899",
                "area": "320.5",
            },
            {
                "name": "Fazenda Alto da Serra",
                "city": "Curitiba",
                "state": "PR",
                "matricula": "PR-00456",
                "car": "PR-CAR-6677",
                "itr": "PR-ITR-7788",
                "ccir": "PR-CCIR-9900",
                "area": "95.7",
            },
            {
                "name": "Fazenda Boa Esperança",
                "city": "Fortaleza",
                "state": "CE",
                "matricula": "CE-00221",
                "car": "CE-CAR-1188",
                "itr": "CE-ITR-2299",
                "ccir": "CE-CCIR-4477",
                "area": "210.0",
            },
        ]

        farms = []
        while len(farms) < count:
            farms.extend(farm_samples)
        farms = farms[:count]

        updated = 0
        idx = 0
        for farm in farms:
            client = pf_clients[idx % len(pf_clients)]
            idx += 1
            line = (
                f"Fazenda: {farm['name']} — {farm['city']}/{farm['state']} — "
                f"Matrícula: {farm['matricula']} — CAR: {farm['car']} — "
                f"ITR: {farm['itr']} — CCIR: {farm['ccir']} — Área: {farm['area']} ha"
            )
            client.notes = (client.notes + "\n" + line) if client.notes else line
            client.save(update_fields=["notes"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {updated} farm notes across PF clients."))