from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.core.files.base import ContentFile
import io
from datetime import datetime


class InvoicePDFGenerator:
    """Gerador de PDF para DANFE (Documento Auxiliar da Nota Fiscal Eletrônica)"""
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        
        # Estilos personalizados
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
    
    def generate_pdf(self):
        """Gera o PDF da DANFE"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=10*mm, bottomMargin=10*mm)
        
        # Elementos do PDF
        elements = []
        
        # Cabeçalho
        elements.append(Paragraph("DANFE", self.title_style))
        elements.append(Paragraph("Documento Auxiliar da Nota Fiscal Eletrônica", self.header_style))
        elements.append(Spacer(1, 10))
        
        # Informações da NF-e
        info_data = [
            ['NÚMERO', 'SÉRIE', 'DATA EMISSÃO', 'TIPO'],
            [
                self.invoice.number,
                self.invoice.series,
                self.invoice.issue_date.strftime('%d/%m/%Y %H:%M'),
                dict(self.invoice.INVOICE_TYPE_CHOICES)[self.invoice.invoice_type]
            ]
        ]
        
        info_table = Table(info_data, colWidths=[40*mm, 30*mm, 50*mm, 60*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 10))
        
        # Chave de Acesso
        if self.invoice.access_key:
            elements.append(Paragraph(f"<b>Chave de Acesso:</b> {self.invoice.access_key}", self.header_style))
            elements.append(Spacer(1, 10))
        
        # Emitente
        elements.append(Paragraph("<b>EMITENTE</b>", self.title_style))
        emit_data = [
            ['Nome/Razão Social', self.invoice.issuer_name],
            ['CNPJ', self.invoice.issuer_tax_id]
        ]
        emit_table = Table(emit_data, colWidths=[50*mm, 130*mm])
        emit_table.setStyle(self._get_table_style())
        elements.append(emit_table)
        elements.append(Spacer(1, 10))
        
        # Destinatário
        client = self.invoice.client
        elements.append(Paragraph("<b>DESTINATÁRIO</b>", self.title_style))
        dest_data = [
            ['Nome/Razão Social', client.name],
            ['CPF/CNPJ', client.tax_id],
            ['Endereço', f"{client.street}, {client.number}"],
            ['Bairro', client.neighborhood],
            ['Cidade/UF', f"{client.city}/{client.state}"],
            ['CEP', client.zip_code],
            ['Email', client.email],
            ['Telefone', client.phone]
        ]
        dest_table = Table(dest_data, colWidths=[50*mm, 130*mm])
        dest_table.setStyle(self._get_table_style())
        elements.append(dest_table)
        elements.append(Spacer(1, 15))
        
        # Itens
        elements.append(Paragraph("<b>ITENS DA NOTA FISCAL</b>", self.title_style))
        
        items_data = [['Cód', 'Descrição', 'Qtd', 'Vl. Unit.', 'Total']]
        
        for item in self.invoice.items.all():
            items_data.append([
                item.code,
                item.description,
                f"{item.quantity:.2f}",
                f"R$ {item.unit_value:.2f}",
                f"R$ {item.total_value:.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[25*mm, 85*mm, 20*mm, 25*mm, 25*mm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 15))
        
        # Totais
        elements.append(Paragraph("<b>VALORES TOTAIS</b>", self.title_style))
        totals_data = [
            ['Base de Cálculo ICMS', f"R$ {self.invoice.icms_base:.2f}"],
            ['Valor do ICMS', f"R$ {self.invoice.icms_value:.2f}"],
            ['Valor do IPI', f"R$ {self.invoice.ipi_value:.2f}"],
            ['Valor do PIS', f"R$ {self.invoice.pis_value:.2f}"],
            ['Valor do COFINS', f"R$ {self.invoice.cofins_value:.2f}"],
            ['Desconto', f"R$ {self.invoice.discount:.2f}"],
            ['Frete', f"R$ {self.invoice.shipping:.2f}"],
            ['VALOR TOTAL DA NOTA', f"R$ {self.invoice.total_value:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[90*mm, 90*mm])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -2), colors.lightgrey),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 15))
        
        # Observações
        if self.invoice.notes:
            elements.append(Paragraph("<b>OBSERVAÇÕES</b>", self.title_style))
            elements.append(Paragraph(self.invoice.notes, self.header_style))
        
        # Rodapé
        elements.append(Spacer(1, 20))
        footer = Paragraph(
            f"Documento emitido por computador. Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(footer)
        
        # Gerar PDF
        doc.build(elements)
        
        # Salvar arquivo
        pdf_content = buffer.getvalue()
        buffer.close()
        
        filename = f"DANFE_{self.invoice.number}_{self.invoice.series}.pdf"
        self.invoice.pdf_file.save(filename, ContentFile(pdf_content))
        
        return pdf_content
    
    def _get_table_style(self):
        """Estilo padrão para tabelas"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ])
