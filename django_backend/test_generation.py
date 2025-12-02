"""
Script para testar geração de XML e PDF de uma nota fiscal
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliza_backend.settings')
django.setup()

from invoices.models import Invoice
from invoices.services.xml_generator import NFeGenerator
from invoices.services.pdf_generator import InvoicePDFGenerator

def test_generation():
    # Pegar a primeira nota
    invoice = Invoice.objects.first()
    
    if not invoice:
        print("❌ Nenhuma nota fiscal encontrada!")
        return
    
    print(f"✅ Testando com nota: {invoice.number}/{invoice.series}")
    print(f"   Cliente: {invoice.client.name}")
    print(f"   Valor: R$ {invoice.total_value}")
    print()
    
    # Testar geração de XML
    try:
        print("🔧 Gerando XML NFe...")
        xml_gen = NFeGenerator(invoice)
        xml_content = xml_gen.generate_xml()
        print(f"✅ XML gerado com sucesso!")
        print(f"   Arquivo: {invoice.xml_file.name if invoice.xml_file else 'N/A'}")
        print()
    except Exception as e:
        print(f"❌ Erro ao gerar XML: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    # Testar geração de PDF
    try:
        print("🔧 Gerando PDF DANFE...")
        pdf_gen = InvoicePDFGenerator(invoice)
        pdf_content = pdf_gen.generate_pdf()
        print(f"✅ PDF gerado com sucesso!")
        print(f"   Arquivo: {invoice.pdf_file.name if invoice.pdf_file else 'N/A'}")
        print()
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        print()

if __name__ == '__main__':
    test_generation()
