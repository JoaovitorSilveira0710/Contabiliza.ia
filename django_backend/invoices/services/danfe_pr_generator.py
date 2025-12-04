"""
Gerador de DANFE - Nota Fiscal do Produtor Rural (Layout SEFAZ-PR)
Baseado no modelo oficial da Secretaria da Fazenda do Estado do Paraná
"""
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


class DANFEParanaGenerator:
    """Gerador de DANFE para Nota Fiscal do Produtor Rural - Padrão SEFAZ-PR"""
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configura os estilos de texto do documento"""
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=2
        )
        
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        self.label_style = ParagraphStyle(
            'Label',
            parent=self.styles['Normal'],
            fontSize=6,
            fontName='Helvetica-Bold',
            textColor=colors.black
        )
        
        self.value_style = ParagraphStyle(
            'Value',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.black
        )
        
        self.small_style = ParagraphStyle(
            'Small',
            parent=self.styles['Normal'],
            fontSize=7,
            fontName='Helvetica'
        )
        
        self.big_style = ParagraphStyle(
            'Big',
            parent=self.styles['Normal'],
            fontSize=20,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
    
    def _format_cpf_cnpj(self, doc):
        """Formata CPF ou CNPJ"""
        doc = ''.join(filter(str.isdigit, doc))
        if len(doc) == 11:  # CPF
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        elif len(doc) == 14:  # CNPJ
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        return doc
    
    def _format_access_key(self, key=None):
        """Formata a chave de acesso com espaços a cada 4 dígitos"""
        if not key:
            key = self.invoice.access_key or '0' * 44
        return ' '.join([key[i:i+4] for i in range(0, len(key), 4)])
    
    def _format_currency(self, value):
        """Formata valor monetário"""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def _format_date(self, date):
        """Formata data"""
        if isinstance(date, str):
            return date
        return date.strftime('%d/%m/%Y %H:%M:%S') if hasattr(date, 'strftime') else str(date)
    
    def generate(self):
        """Gera o PDF do DANFE e retorna o conteúdo (sem salvar no banco)"""
        print("    [PDF] Criando buffer...")
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=5*mm,
            bottomMargin=5*mm,
            leftMargin=5*mm,
            rightMargin=5*mm
        )
        print("    [PDF] Buffer criado")
        
        elements = []
        
        # Cabeçalho principal
        print("    [PDF] Construindo cabeçalho...")
        elements.extend(self._build_header())
        elements.append(Spacer(1, 3*mm))
        
        # Dados da operação
        print("    [PDF] Construindo dados da operação...")
        elements.extend(self._build_operation_data())
        elements.append(Spacer(1, 2*mm))
        
        # Emitente
        print("    [PDF] Construindo dados do emitente...")
        elements.extend(self._build_issuer_data())
        elements.append(Spacer(1, 2*mm))
        
        # Destinatário/Remetente
        print("    [PDF] Construindo dados do destinatário...")
        elements.extend(self._build_receiver_data())
        elements.append(Spacer(1, 2*mm))
        
        # Cálculo do Imposto
        print("    [PDF] Construindo cálculo de impostos...")
        elements.extend(self._build_tax_calculation())
        elements.append(Spacer(1, 2*mm))
        
        # Transporte
        print("    [PDF] Construindo dados de transporte...")
        elements.extend(self._build_transport_data())
        elements.append(Spacer(1, 2*mm))
        
        # Produtos/Serviços
        print("    [PDF] Construindo tabela de produtos...")
        elements.extend(self._build_items_table())
        elements.append(Spacer(1, 2*mm))
        
        # Cálculo do ISSQN
        print("    [PDF] Construindo cálculo de ISSQN...")
        elements.extend(self._build_issqn_calculation())
        elements.append(Spacer(1, 2*mm))
        
        # Dados Adicionais
        print("    [PDF] Construindo dados adicionais...")
        elements.extend(self._build_additional_data())
        
        # Build PDF
        print("    [PDF] Gerando documento final...")
        doc.build(elements)
        print("    [PDF] Documento gerado")
        
        pdf_content = buffer.getvalue()
        buffer.close()
        print("    [PDF] Buffer fechado")
        
        return pdf_content
    
    def generate_pdf(self):
        """Gera o PDF do DANFE"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=5*mm,
            bottomMargin=5*mm,
            leftMargin=5*mm,
            rightMargin=5*mm
        )
        
        elements = []
        
        # Cabeçalho principal
        elements.extend(self._build_header())
        elements.append(Spacer(1, 3*mm))
        
        # Dados da operação
        elements.extend(self._build_operation_data())
        elements.append(Spacer(1, 2*mm))
        
        # Emitente
        elements.extend(self._build_issuer_data())
        elements.append(Spacer(1, 2*mm))
        
        # Destinatário/Remetente
        elements.extend(self._build_receiver_data())
        elements.append(Spacer(1, 2*mm))
        
        # Cálculo do Imposto
        elements.extend(self._build_tax_calculation())
        elements.append(Spacer(1, 2*mm))
        
        # Transporte
        elements.extend(self._build_transport_data())
        elements.append(Spacer(1, 2*mm))
        
        # Produtos/Serviços
        elements.extend(self._build_items_table())
        elements.append(Spacer(1, 2*mm))
        
        # Cálculo do ISSQN
        elements.extend(self._build_issqn_calculation())
        elements.append(Spacer(1, 2*mm))
        
        # Dados Adicionais
        elements.extend(self._build_additional_data())
        
        # Build PDF
        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Salvar arquivo
        filename = f"DANFE_NF{self.invoice.number}_Serie{self.invoice.series}.pdf"
        self.invoice.pdf_file.save(filename, ContentFile(pdf_content))
        
        return pdf_content
    
    def _build_header(self):
        """Constrói o cabeçalho do DANFE"""
        elements = []
        
        # Linha 1: Logo + Identificação + NF-e + DANFE
        header_data = [
            [
                # Coluna 1: Logo e identificação do estado
                Paragraph('<b>Estado do Paraná</b><br/><font size=7>Secretaria da Fazenda</font><br/><font size=6>Nota Fiscal do Produtor Rural Eletrônica</font>', self.header_style),
                # Coluna 2: Dados da NF-e
                Paragraph(f'<b>NF-e</b><br/><b>Nº:</b> {self.invoice.number}<br/><b>SÉRIE:</b> {self.invoice.series}', self.value_style),
                # Coluna 3: DANFE
                Paragraph('<b>DANFE</b><br/><font size=6>Documento Auxiliar da Nota</font><br/><font size=6>Fiscal Eletrônica</font><br/><b>0 - ENTRADA</b><br/><b>1 - SAÍDA</b>', self.header_style),
                # Coluna 4: Tipo de operação
                Paragraph(f'<b>{self.invoice.operation_type[0] if self.invoice.operation_type else "1"}</b>', self.big_style)
            ]
        ]
        
        header_table = Table(header_data, colWidths=[60*mm, 40*mm, 50*mm, 20*mm])
        header_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
        ]))
        elements.append(header_table)
        
        # Chave de Acesso
        access_key = self.invoice.access_key or ('0' * 44)
        formatted_key = self._format_access_key(access_key)
        
        key_data = [
            [Paragraph('<b>CHAVE DE ACESSO</b>', self.label_style)],
            [Paragraph(formatted_key, self.value_style)]
        ]
        
        key_table = Table(key_data, colWidths=[190*mm])
        key_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
        ]))
        elements.append(key_table)
        
        # Código de Barras
        try:
            barcode = code128.Code128(access_key, barHeight=15*mm, barWidth=0.33*mm)
            drawing = Drawing(190*mm, 18*mm)
            drawing.add(barcode)
            elements.append(drawing)
        except:
            elements.append(Paragraph(f'[CÓDIGO DE BARRAS: {access_key}]', self.small_style))
        
        # Consulta de autenticidade e protocolo
        info_data = [
            [
                Paragraph('<font size=6>Consulta de autenticidade no portal nacional da NF-e</font><br/><font size=6>www.nfe.fazenda.gov.br/portal ou no site da Sefaz</font><br/><font size=6>Autorizada</font>', self.small_style),
                Paragraph(f'<b>PROTOCOLO DE AUTORIZAÇÃO DE USO</b><br/>{self.invoice.protocol or "Aguardando autorização"}<br/>{self._format_date(self.invoice.authorization_date) if self.invoice.authorization_date else ""}', self.value_style)
            ]
        ]
        
        info_table = Table(info_data, colWidths=[95*mm, 95*mm])
        info_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        
        return elements
    
    def _build_operation_data(self):
        """Constrói dados da operação"""
        elements = []
        
        data = [
            [
                Paragraph('<b>NATUREZA DA OPERAÇÃO</b>', self.label_style),
                Paragraph('<b>INSCRIÇÃO ESTADUAL</b>', self.label_style),
                Paragraph('<b>INSC. EST. DO SUBST. TRIBUTÁRIO</b>', self.label_style)
            ],
            [
                Paragraph(dict(self.invoice._meta.get_field('operation_nature').choices).get(self.invoice.operation_nature, 'Venda'), self.value_style),
                Paragraph(self.invoice.issuer_state_registration or '-', self.value_style),
                Paragraph('-', self.value_style)
            ]
        ]
        
        table = Table(data, colWidths=[80*mm, 55*mm, 55*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(table)
        
        return elements
    
    def _build_issuer_data(self):
        """Constrói dados do emitente"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>EMITENTE</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Dados
        data = [
            [
                Paragraph('<b>NOME/RAZÃO SOCIAL</b>', self.label_style),
                Paragraph(self.invoice.issuer_name or '-', self.value_style)
            ],
            [
                Paragraph('<b>Endereço</b>', self.label_style),
                Paragraph(f"{self.invoice.issuer_address or ''}, {self.invoice.issuer_number or ''} {self.invoice.issuer_district or ''}".strip(), self.value_style)
            ],
            [
                Paragraph('<b>BAIRRO/DISTRITO</b>', self.label_style),
                Paragraph(f"{self.invoice.issuer_district or ''} - {self.invoice.issuer_state or ''}", self.value_style),
                Paragraph('<b>CEP</b>', self.label_style),
                Paragraph(self.invoice.issuer_zip_code or '-', self.value_style)
            ],
            [
                Paragraph('<b>MUNICÍPIO</b>', self.label_style),
                Paragraph(self.invoice.issuer_city or '-', self.value_style),
                Paragraph('<b>FONE/FAX</b>', self.label_style),
                Paragraph(self.invoice.issuer_phone or '-', self.value_style)
            ]
        ]
        
        table = Table(data, colWidths=[30*mm, 100*mm, 20*mm, 40*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 2), (2, -1), colors.lightgrey),
        ]))
        elements.append(table)
        
        return elements
    
    def _build_receiver_data(self):
        """Constrói dados do destinatário/remetente"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>DESTINATÁRIO/REMETENTE</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Dados
        client = self.invoice.client
        data = [
            [
                Paragraph('<b>NOME/RAZÃO SOCIAL</b>', self.label_style),
                Paragraph(client.name or self.invoice.receiver_name or '-', self.value_style),
                Paragraph('<b>CNPJ/CPF</b>', self.label_style),
                Paragraph(self._format_cpf_cnpj(client.tax_id or self.invoice.receiver_tax_id or ''), self.value_style),
                Paragraph('<b>DATA DE EMISSÃO</b>', self.label_style),
                Paragraph(self._format_date(self.invoice.issue_date), self.value_style)
            ],
            [
                Paragraph('<b>ENDEREÇO</b>', self.label_style),
                Paragraph(f"{client.street or self.invoice.receiver_address or ''}, {client.number or self.invoice.receiver_number or ''}".strip(), self.value_style),
                Paragraph('<b>BAIRRO/DISTRITO</b>', self.label_style),
                Paragraph(client.neighborhood or self.invoice.receiver_district or '-', self.value_style),
                Paragraph('<b>CEP</b>', self.label_style),
                Paragraph(client.zip_code or self.invoice.receiver_zip_code or '-', self.value_style)
            ],
            [
                Paragraph('<b>MUNICÍPIO</b>', self.label_style),
                Paragraph(client.city or self.invoice.receiver_city or '-', self.value_style),
                Paragraph('<b>FONE/FAX</b>', self.label_style),
                Paragraph(client.phone or self.invoice.receiver_phone or '-', self.value_style),
                Paragraph('<b>UF</b>', self.label_style),
                Paragraph(client.state or self.invoice.receiver_state or '-', self.value_style)
            ],
            [
                Paragraph('<b>INSCRIÇÃO ESTADUAL</b>', self.label_style),
                Paragraph(client.state_registration or self.invoice.receiver_state_registration or '-', self.value_style),
                Paragraph('<b>DATA DE ENTRADA/SAÍDA</b>', self.label_style),
                Paragraph(self._format_date(self.invoice.issue_date), self.value_style)
            ]
        ]
        
        table = Table(data, colWidths=[30*mm, 60*mm, 30*mm, 30*mm, 20*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
        ]))
        elements.append(table)
        
        return elements
    
    def _build_tax_calculation(self):
        """Constrói o cálculo do imposto"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>CÁLCULO DO IMPOSTO</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Linha 1
        data = [
            [
                Paragraph('<b>BASE DE CÁLCULO DO ICMS</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.icms_base), self.value_style),
                Paragraph('<b>VALOR DO ICMS</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.icms_value), self.value_style),
                Paragraph('<b>BASE DE CÁLCULO ICMS ST</b>', self.label_style),
                Paragraph('R$ 0,00', self.value_style),
                Paragraph('<b>VALOR DO ICMS ST</b>', self.label_style),
                Paragraph('R$ 0,00', self.value_style),
                Paragraph('<b>VALOR TOTAL DOS PRODUTOS</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.total_products), self.value_style)
            ]
        ]
        
        table = Table(data, colWidths=[28*mm, 15*mm, 20*mm, 15*mm, 28*mm, 15*mm, 22*mm, 15*mm, 22*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
            ('BACKGROUND', (6, 0), (6, -1), colors.lightgrey),
            ('BACKGROUND', (8, 0), (8, -1), colors.lightgrey),
        ]))
        elements.append(table)
        
        # Linha 2
        data2 = [
            [
                Paragraph('<b>VALOR DO FRETE</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.shipping), self.value_style),
                Paragraph('<b>VALOR DO SEGURO</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.insurance), self.value_style),
                Paragraph('<b>DESCONTO</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.discount), self.value_style),
                Paragraph('<b>OUTRAS DESPESAS ACESSÓRIAS</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.other_expenses), self.value_style),
                Paragraph('<b>VALOR DO IPI</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.ipi_value), self.value_style),
                Paragraph('<b>VALOR TOTAL DA NOTA</b>', self.label_style),
                Paragraph(f'<b>{self._format_currency(self.invoice.total_value)}</b>', self.value_style)
            ]
        ]
        
        table2 = Table(data2, colWidths=[20*mm, 15*mm, 20*mm, 15*mm, 15*mm, 15*mm, 25*mm, 15*mm, 18*mm, 15*mm, 22*mm, 20*mm])
        table2.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, 0), colors.lightgrey),
            ('BACKGROUND', (4, 0), (4, 0), colors.lightgrey),
            ('BACKGROUND', (6, 0), (6, 0), colors.lightgrey),
            ('BACKGROUND', (8, 0), (8, 0), colors.lightgrey),
            ('BACKGROUND', (10, 0), (10, 0), colors.lightgrey),
        ]))
        elements.append(table2)
        
        return elements
    
    def _build_transport_data(self):
        """Constrói dados do transporte"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>TRANSPORTADOR/VOLUMES TRANSPORTADOS</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Modalidade do frete
        freight_desc = dict(self.invoice._meta.get_field('freight_mode').choices).get(
            self.invoice.freight_mode, 
            '9-Sem frete'
        )
        
        # Dados
        data = [
            [
                Paragraph('<b>RAZÃO SOCIAL</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>FRETE POR CONTA</b>', self.label_style),
                Paragraph(freight_desc, self.value_style),
                Paragraph('<b>CÓDIGO ANTT</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>PLACA DO VEÍCULO</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>UF</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>CNPJ/CPF</b>', self.label_style),
                Paragraph('-', self.value_style)
            ],
            [
                Paragraph('<b>ENDEREÇO</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>MUNICÍPIO</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>UF</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>INSCRIÇÃO ESTADUAL</b>', self.label_style),
                Paragraph('-', self.value_style)
            ],
            [
                Paragraph('<b>QUANTIDADE</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>ESPÉCIE</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>MARCA</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>NUMERAÇÃO</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>PESO BRUTO</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>PESO LÍQUIDO</b>', self.label_style),
                Paragraph('-', self.value_style)
            ]
        ]
        
        table = Table(data, colWidths=[20*mm, 30*mm, 20*mm, 25*mm, 15*mm, 15*mm, 20*mm, 15*mm, 10*mm, 10*mm, 15*mm, 15*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
            ('BACKGROUND', (6, 0), (6, -1), colors.lightgrey),
            ('BACKGROUND', (8, 0), (8, -1), colors.lightgrey),
            ('BACKGROUND', (10, 0), (10, -1), colors.lightgrey),
        ]))
        elements.append(table)
        
        return elements
    
    def _build_items_table(self):
        """Constrói a tabela de produtos/serviços"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>DADOS DOS PRODUTOS/SERVIÇOS</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Cabeçalho da tabela
        headers = [
            Paragraph('<b>CÓDIGO<br/>PRODUTO</b>', self.label_style),
            Paragraph('<b>DESCRIÇÃO DO<br/>PRODUTO/SERVIÇOS</b>', self.label_style),
            Paragraph('<b>NCM/SH</b>', self.label_style),
            Paragraph('<b>CST</b>', self.label_style),
            Paragraph('<b>CFOP</b>', self.label_style),
            Paragraph('<b>UNID</b>', self.label_style),
            Paragraph('<b>QUANTIDADE</b>', self.label_style),
            Paragraph('<b>VALOR<br/>UNITÁRIO</b>', self.label_style),
            Paragraph('<b>VALOR<br/>TOTAL</b>', self.label_style),
            Paragraph('<b>BASE<br/>CÁLC. ICMS</b>', self.label_style),
            Paragraph('<b>ALÍQ.<br/>ICMS</b>', self.label_style),
            Paragraph('<b>VALOR<br/>ICMS</b>', self.label_style),
            Paragraph('<b>ALÍQ.<br/>IPI</b>', self.label_style),
            Paragraph('<b>VALOR<br/>IPI</b>', self.label_style)
        ]
        
        data = [headers]
        
        # Adicionar itens
        for item in self.invoice.items.all():
            data.append([
                Paragraph(str(item.code), self.small_style),
                Paragraph(item.description[:30], self.small_style),
                Paragraph(item.ncm or '-', self.small_style),
                Paragraph(item.icms_cst or '-', self.small_style),
                Paragraph(item.cfop or '-', self.small_style),
                Paragraph(item.unit, self.small_style),
                Paragraph(f"{item.quantity:.4f}".rstrip('0').rstrip('.'), self.small_style),
                Paragraph(f"{item.unit_value:.2f}", self.small_style),
                Paragraph(f"{item.total_value:.2f}", self.small_style),
                Paragraph(f"{item.total_value:.2f}", self.small_style),  # Base ICMS aproximada
                Paragraph(f"{item.icms_rate:.2f}", self.small_style),
                Paragraph(f"{item.icms_value:.2f}", self.small_style),
                Paragraph(f"{item.ipi_rate:.2f}", self.small_style),
                Paragraph(f"{item.ipi_value:.2f}", self.small_style)
            ])
        
        # Se não houver itens
        if len(data) == 1:
            data.append([
                Paragraph('-', self.small_style),
                Paragraph('Nenhum item cadastrado', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style),
                Paragraph('-', self.small_style)
            ])
        
        col_widths = [12*mm, 35*mm, 12*mm, 8*mm, 10*mm, 8*mm, 15*mm, 13*mm, 13*mm, 13*mm, 10*mm, 13*mm, 10*mm, 13*mm]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        
        return elements
    
    def _build_issqn_calculation(self):
        """Constrói o cálculo do ISSQN"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>CÁLCULO DO ISSQN</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Dados
        data = [
            [
                Paragraph('<b>INSCRIÇÃO MUNICIPAL</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>VALOR TOTAL DOS SERVIÇOS</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.total_services), self.value_style),
                Paragraph('<b>BASE DE CÁLCULO DO ISSQN</b>', self.label_style),
                Paragraph('-', self.value_style),
                Paragraph('<b>VALOR DO ISSQN</b>', self.label_style),
                Paragraph(self._format_currency(self.invoice.iss_value), self.value_style)
            ]
        ]
        
        table = Table(data, colWidths=[30*mm, 25*mm, 35*mm, 25*mm, 35*mm, 20*mm, 20*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, 0), colors.lightgrey),
            ('BACKGROUND', (4, 0), (4, 0), colors.lightgrey),
            ('BACKGROUND', (6, 0), (6, 0), colors.lightgrey),
        ]))
        elements.append(table)
        
        return elements
    
    def _build_additional_data(self):
        """Constrói dados adicionais"""
        elements = []
        
        # Título
        title_data = [[Paragraph('<b>DADOS ADICIONAIS</b>', self.header_style)]]
        title_table = Table(title_data, colWidths=[190*mm])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(title_table)
        
        # Informações complementares
        additional_info = self.invoice.additional_info or 'Sem dados adicionais'
        notes = self.invoice.notes or ''
        
        combined_info = f"{additional_info}"
        if notes:
            combined_info += f"\n{notes}"
        
        data = [
            [
                Paragraph('<b>INFORMAÇÕES COMPLEMENTARES</b>', self.label_style),
                Paragraph('<b>RESERVADO AO FISCO</b>', self.label_style)
            ],
            [
                Paragraph(combined_info, self.small_style),
                Paragraph('-', self.small_style)
            ]
        ]
        
        table = Table(data, colWidths=[130*mm, 60*mm], rowHeights=[7*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(table)
        
        return elements
