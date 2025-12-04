from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from django.core.files.base import ContentFile
import io
from datetime import datetime


class InvoicePDFGenerator:
    """Gerador de PDF para DANFE - Nota Fiscal do Produtor Rural (Layout SEFAZ-PR)"""
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        
        # Estilos personalizados conforme layout DANFE
        self.title_style = ParagraphStyle(
            'DANFETitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceAfter=3,
            alignment=TA_CENTER
        )
        
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            spaceAfter=3,
            fontName='Helvetica'
        )
        
        self.field_label_style = ParagraphStyle(
            'FieldLabel',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        self.field_value_style = ParagraphStyle(
            'FieldValue',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica'
        )
    
    def generate_pdf(self):
        """Gera o PDF da DANFE com layout mais aderente ao modelo oficial."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=6*mm, bottomMargin=8*mm, leftMargin=8*mm, rightMargin=8*mm)

        elements = []

        # Cabeçalho consolidado (título + dados NF + chave + barcode)
        elements.extend(self._build_header_block())
        elements.append(Spacer(1, 2*mm))

        # Quadro emitente + quadro destinatário
        elements.extend(self._build_parties_block())
        elements.append(Spacer(1, 2*mm))

        # Dados de operação (natureza, data/hora, protocolo)
        elements.extend(self._build_operation_block())
        elements.append(Spacer(1, 2*mm))

        # Itens (tabela padrão)
        elements.extend(self._build_items_block())
        elements.append(Spacer(1, 2*mm))

        # Totais/impostos
        elements.extend(self._build_totals_block())
        elements.append(Spacer(1, 2*mm))

        # Informações adicionais
        elements.extend(self._build_additional_info_block())
        elements.append(Spacer(1, 2*mm))

        # Canhoto de recebimento
        elements.extend(self._build_receipt_block())

        # Rodapé
        elements.append(Spacer(1, 4*mm))
        footer = Paragraph(
            f"Documento emitido eletronicamente - Contabiliza.IA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)
        )
        elements.append(footer)

        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()

        filename = f"DANFE_{self.invoice.number}_{self.invoice.series}.pdf"
        self.invoice.pdf_file.save(filename, ContentFile(pdf_content))
        return pdf_content

    # ===================== BLOCO CABEÇALHO =====================
    def _format_access_key(self):
        key = self.invoice.access_key or ('0' * 44)
        return ' '.join([key[i:i+4] for i in range(0, len(key), 4)])

    def _barcode_drawing(self, key):
        # Fallback: se Code128 não puder ser embutido no Drawing, retorna Paragraph informativo
        try:
            bc = code128.Code128(key, barHeight=12*mm, barWidth=0.28*mm)
            drawing = Drawing(180*mm, 15*mm)
            # Alguns builds do reportlab exigem add() direto
            drawing.add(bc)
            return drawing
        except Exception:
            return Paragraph(f"<b>[BARCODE]</b> {key}", self.field_value_style)

    def _build_header_block(self):
        elements = []
        formatted_key = self._format_access_key()
        key_raw = self.invoice.access_key or ('0' * 44)
        # Linha superior: DANFE + página (simplificado: sempre 1/1)
        header_data = [
            [Paragraph('<b>DANFE</b><br/><font size=6>Documento Auxiliar da Nota Fiscal Eletrônica</font>', self.field_value_style),
             Paragraph(f'<b>NF-e Nº:</b> {self.invoice.number}<br/><b>Série:</b> {self.invoice.series}<br/><b>Página:</b> 1/1', self.field_value_style)]
        ]
        table = Table(header_data, colWidths=[120*mm, 60*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)

        # Chave de acesso + barcode
        key_data = [[Paragraph('<b>CHAVE DE ACESSO</b>', self.field_label_style)], [Paragraph(formatted_key, self.field_value_style)], [self._barcode_drawing(key_raw)]]
        key_table = Table(key_data, colWidths=[180*mm])
        key_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(key_table)
        return elements

    # ===================== PARTES (EMITENTE/DEST) =====================
    def _build_parties_block(self):
        elements = []
        client = self.invoice.client
        emit_html = f"""<b>EMITENTE</b><br/>{self.invoice.issuer_name}<br/>CNPJ: {self.invoice.issuer_tax_id}"""
        dest_html = f"""<b>DESTINATÁRIO</b><br/>{client.name}<br/>CPF/CNPJ: {client.tax_id}<br/>Endereço: {client.street}, {client.number} - {client.neighborhood} - {client.city}/{client.state} - CEP: {client.zip_code}"""
        parties_data = [[Paragraph(emit_html, self.field_value_style), Paragraph(dest_html, self.field_value_style)]]
        parties_table = Table(parties_data, colWidths=[90*mm, 90*mm])
        parties_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.7, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(parties_table)
        return elements

    # ===================== DADOS OPERAÇÃO =====================
    def _build_operation_block(self):
        elements = []
        natureza = getattr(self.invoice, 'additional_info', '') or 'NATUREZA DA OPERAÇÃO'
        op_data = [
            [Paragraph('<b>NATUREZA DA OPERAÇÃO</b><br/>' + natureza, self.field_value_style),
             Paragraph('<b>DATA/HORA EMISSÃO</b><br/>' + self.invoice.issue_date.strftime('%d/%m/%Y %H:%M:%S'), self.field_value_style),
             Paragraph('<b>PROTOCOLO AUTORIZAÇÃO</b><br/>' + (self.invoice.protocol or '-'), self.field_value_style)]
        ]
        op_table = Table(op_data, colWidths=[90*mm, 45*mm, 45*mm])
        op_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.7, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]))
        elements.append(op_table)
        return elements

    # ===================== ITENS =====================
    def _build_items_block(self):
        elements = []
        header = ['cProd', 'xProd', 'NCM', 'CFOP', 'uCom', 'qCom', 'vUnCom', 'vProd', 'vBC', 'vICMS', 'vIPI']
        rows = [header]
        for item in self.invoice.items.all():
            rows.append([
                item.code,
                item.description[:25] + ('...' if len(item.description) > 25 else ''),
                item.ncm or '-',
                item.cfop,
                item.unit,
                f"{item.quantity:.2f}",
                f"{item.unit_value:.2f}",
                f"{item.total_value:.2f}",
                f"{item.total_value:.2f}",  # vBC (aprox total item)
                f"{item.icms_value:.2f}",
                f"{item.ipi_value:.2f}"
            ])
        if len(rows) == 1:
            rows.append(['-', 'Nenhum item', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
        col_widths = [16*mm, 32*mm, 10*mm, 10*mm, 10*mm, 12*mm, 16*mm, 16*mm, 14*mm, 14*mm, 14*mm]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.6, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        return elements

    # ===================== TOTAIS =====================
    def _build_totals_block(self):
        elements = []
        t = self.invoice
        data = [
            [Paragraph('<b>Base ICMS</b><br/>' + f"R$ {t.icms_base:.2f}", self.field_value_style),
             Paragraph('<b>Valor ICMS</b><br/>' + f"R$ {t.icms_value:.2f}", self.field_value_style),
             Paragraph('<b>Base ICMS ST</b><br/>R$ 0,00', self.field_value_style),
             Paragraph('<b>Valor ICMS ST</b><br/>R$ 0,00', self.field_value_style),
             Paragraph('<b>Valor Produtos</b><br/>' + f"R$ {t.total_products:.2f}", self.field_value_style)],
            [Paragraph('<b>Frete</b><br/>' + f"R$ {t.shipping:.2f}", self.field_value_style),
             Paragraph('<b>Seguro</b><br/>' + f"R$ {t.insurance:.2f}", self.field_value_style),
             Paragraph('<b>Desconto</b><br/>' + f"R$ {t.discount:.2f}", self.field_value_style),
             Paragraph('<b>Outras Desp.</b><br/>' + f"R$ {t.other_expenses:.2f}", self.field_value_style),
             Paragraph('<b>Valor IPI</b><br/>' + f"R$ {t.ipi_value:.2f}", self.field_value_style)],
            [Paragraph('<b>Valor Total da NF</b>', self.field_label_style), '', '', '', Paragraph(f"R$ {t.total_value:.2f}", ParagraphStyle('TotNF', parent=self.field_value_style, fontSize=10, fontName='Helvetica-Bold'))]
        ]
        table = Table(data, colWidths=[36*mm, 36*mm, 36*mm, 36*mm, 36*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('INNERGRID', (0, 0), (-1, -2), 0.5, colors.black),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('SPAN', (0, 2), (3, 2)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]))
        elements.append(table)
        return elements

    # ===================== INFO ADICIONAL =====================
    def _build_additional_info_block(self):
        elements = []
        info = self.invoice.notes or 'Sem informações complementares.'
        fisco = 'Reservado ao Fisco'
        data = [[Paragraph('<b>INFORMAÇÕES COMPLEMENTARES</b><br/>' + info, self.field_value_style), Paragraph('<b>RESERVADO AO FISCO</b><br/>' + fisco, self.field_value_style)]]
        table = Table(data, colWidths=[120*mm, 60*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.7, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        return elements

    # ===================== CANHOTO =====================
    def _build_receipt_block(self):
        elements = []
        txt = ('Recebemos de ' + self.invoice.issuer_name + ' os produtos/mercadorias constantes da NF-e indicada ' \
               'abaixo. Em ' + datetime.now().strftime('%d/%m/%Y') + '. ______________________________________ Assinatura')
        receipt = Paragraph('<b>RECIBO DO DESTINATÁRIO</b><br/>' + txt, ParagraphStyle('Rec', parent=self.field_value_style, fontSize=7))
        box = Table([[receipt]], colWidths=[180*mm])
        box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(box)
        return elements
    
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
