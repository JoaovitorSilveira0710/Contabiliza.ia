from pathlib import Path
import shutil
from django.conf import settings


def _safe_copy(src_path: Path, dest_path: Path) -> bool:
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
        return True
    except Exception:
        return False


def backup_invoice_files(invoice) -> dict:
    """
    Copy invoice XML and PDF files to the backups folder, preserving a predictable structure.
    Returns a dict with backup paths that were created.
    """
    results = {"xml": None, "pdf": None}

    base_backup_dir = Path(getattr(settings, 'BACKUP_DIR', Path(settings.BASE_DIR).parent / 'backups'))
    inv_dir = base_backup_dir / 'invoices' / str(invoice.issue_date.year) / f"{invoice.issue_date.month:02d}"

    # Backup XML
    if invoice.xml_file and invoice.xml_file.name:
        src_xml = Path(settings.MEDIA_ROOT) / invoice.xml_file.name
        if src_xml.exists():
            dest_xml = inv_dir / 'xml' / Path(invoice.xml_file.name).name
            if _safe_copy(src_xml, dest_xml):
                results["xml"] = str(dest_xml)

    # Backup PDF
    if invoice.pdf_file and invoice.pdf_file.name:
        src_pdf = Path(settings.MEDIA_ROOT) / invoice.pdf_file.name
        if src_pdf.exists():
            dest_pdf = inv_dir / 'pdf' / Path(invoice.pdf_file.name).name
            if _safe_copy(src_pdf, dest_pdf):
                results["pdf"] = str(dest_pdf)

    return results
