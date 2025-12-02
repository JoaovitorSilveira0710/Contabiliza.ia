from django.core.management.base import BaseCommand
from django.conf import settings
from invoices.models import Invoice
from invoices.services.backup_service import backup_invoice_files
from pathlib import Path


class Command(BaseCommand):
    help = 'Backup all invoice XML/PDF files to BACKUP_DIR preserving structure'

    def add_arguments(self, parser):
        parser.add_argument('--only-with-files', action='store_true', help='Backup only invoices that already have XML/PDF')
        parser.add_argument('--year', type=int, help='Filter by issue year')
        parser.add_argument('--month', type=int, help='Filter by issue month (1-12)')

    def handle(self, *args, **options):
        qs = Invoice.objects.all()
        if options.get('year'):
            qs = qs.filter(issue_date__year=options['year'])
        if options.get('month'):
            qs = qs.filter(issue_date__month=options['month'])
        if options.get('only_with_files'):
            qs = qs.exclude(xml_file='').exclude(xml_file=None) | qs.exclude(pdf_file='').exclude(pdf_file=None)

        total = qs.count()
        self.stdout.write(self.style.WARNING(f'Backing up {total} invoices...'))
        ok, fail = 0, 0
        for inv in qs.iterator():
            res = backup_invoice_files(inv)
            if res.get('xml') or res.get('pdf'):
                ok += 1
                self.stdout.write(self.style.SUCCESS(f'#{inv.id} NF {inv.number} -> XML:{bool(res.get("xml"))} PDF:{bool(res.get("pdf"))}'))
            else:
                fail += 1
                self.stdout.write(self.style.ERROR(f'#{inv.id} NF {inv.number} -> nothing to backup'))

        backup_dir = Path(getattr(settings, 'BACKUP_DIR', Path(settings.BASE_DIR).parent / 'backups'))
        self.stdout.write(self.style.SUCCESS(f'Done. OK: {ok} | Fail: {fail} | Backup dir: {backup_dir}'))
