"""
Gerador de DANFE usando FPDF2 - Versão otimizada e rápida
Muito mais leve que ReportLab
"""
from fpdf import FPDF
from decimal import Decimal
from datetime import datetime
import io


class DANFEFpdfGenerator:
    """Gerador de DANFE usando FPDF2 - Versão rápida"""
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')
        self.pdf.set_auto_page_break(auto=True, margin=10)
        self.pdf.add_page()
        
    def _format_currency(self, value):
        """Formata valor monetário"""
        if value is None:
            value = 0
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def _format_cpf_cnpj(self, doc):
        """Formata CPF ou CNPJ"""
        if not doc:
            return ''
        doc = ''.join(filter(str.isdigit, str(doc)))
        if len(doc) == 11:  # CPF
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        elif len(doc) == 14:  # CNPJ
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        return doc
    
    def _format_date(self, date):
        """Formata data"""
        if isinstance(date, str):
            return date
        if hasattr(date, 'strftime'):
            return date.strftime('%d/%m/%Y')
        return str(date)
    
    def _build_header(self):
        """Constrói o cabeçalho do DANFE"""
        # Título
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'DANFE - Documento Auxiliar da Nota Fiscal Eletrônica', 0, 1, 'C')
        
        self.pdf.set_font('Arial', '', 8)
        self.pdf.cell(0, 5, 'Não é documento fiscal - Simples representação da NF-e', 0, 1, 'C')
        self.pdf.ln(3)
        
    def _build_issuer_receiver(self):
        """Constrói dados do emitente e destinatário"""
        # Box Emitente
        y_start = self.pdf.get_y()
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.cell(95, 5, 'EMITENTE', 1, 0)
        self.pdf.cell(95, 5, 'DESTINATÁRIO/REMETENTE', 1, 1)
        
        # Dados do Emitente
        self.pdf.set_font('Arial', '', 8)
        y_start = self.pdf.get_y()
        
        # Coluna Emitente
        self.pdf.set_xy(10, y_start)
        emitente_info = [
            f"Nome: {self.invoice.issuer_name or ''}",
            f"CNPJ: {self._format_cpf_cnpj(self.invoice.issuer_tax_id)}",
            f"IE: {self.invoice.issuer_state_registration or ''}",
            f"Endereço: {self.invoice.issuer_address or ''}, {self.invoice.issuer_number or ''}",
            f"Bairro: {self.invoice.issuer_district or ''} - {self.invoice.issuer_city or ''}/{self.invoice.issuer_state or ''}",
            f"CEP: {self.invoice.issuer_zip_code or ''} Fone: {self.invoice.issuer_phone or ''}"
        ]
        
        for line in emitente_info:
            self.pdf.cell(95, 4, line[:60], 1, 0)
            self.pdf.cell(0, 4, '', 0, 1)
        
        # Coluna Destinatário
        y_end = self.pdf.get_y()
        self.pdf.set_xy(105, y_start)
        
        destinatario_info = [
            f"Nome: {self.invoice.receiver_name or ''}",
            f"CNPJ/CPF: {self._format_cpf_cnpj(self.invoice.receiver_tax_id)}",
            f"IE: {self.invoice.receiver_state_registration or ''}",
            f"Endereço: {self.invoice.receiver_address or ''}, {self.invoice.receiver_number or ''}",
            f"Bairro: {self.invoice.receiver_district or ''} - {self.invoice.receiver_city or ''}/{self.invoice.receiver_state or ''}",
            f"CEP: {self.invoice.receiver_zip_code or ''} Fone: {self.invoice.receiver_phone or ''}"
        ]
        
        for line in destinatario_info:
            self.pdf.cell(95, 4, line[:60], 1, 1)
        
        self.pdf.set_y(max(y_end, self.pdf.get_y()))
        self.pdf.ln(2)
        
    def _build_invoice_data(self):
        """Constrói dados da nota fiscal"""
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.cell(0, 5, 'DADOS DA NOTA FISCAL', 1, 1, 'C')
        
        self.pdf.set_font('Arial', '', 8)
        data = [
            f"Número: {self.invoice.number}",
            f"Série: {self.invoice.series}",
            f"Data Emissão: {self._format_date(self.invoice.issue_date)}",
            f"Natureza: {self.invoice.operation_nature or 'Venda'}",
            f"CFOP: {self.invoice.cfop or ''}",
        ]
        
        # Duas colunas
        for i in range(0, len(data), 2):
            if i < len(data):
                self.pdf.cell(95, 5, data[i], 1, 0)
            if i + 1 < len(data):
                self.pdf.cell(95, 5, data[i + 1], 1, 1)
            else:
                self.pdf.cell(95, 5, '', 1, 1)
        
        self.pdf.ln(2)
        
    def _build_items_table(self):
        """Constrói tabela de produtos/serviços"""
        self.pdf.set_font('Arial', 'B', 8)
        self.pdf.cell(0, 5, 'PRODUTOS / SERVIÇOS', 1, 1, 'C')
        
        # Cabeçalho da tabela
        self.pdf.cell(10, 5, 'Item', 1, 0, 'C')
        self.pdf.cell(60, 5, 'Descrição', 1, 0, 'C')
        self.pdf.cell(20, 5, 'NCM', 1, 0, 'C')
        self.pdf.cell(20, 5, 'Qtd', 1, 0, 'C')
        self.pdf.cell(15, 5, 'Un', 1, 0, 'C')
        self.pdf.cell(30, 5, 'Valor Unit.', 1, 0, 'C')
        self.pdf.cell(35, 5, 'Valor Total', 1, 1, 'C')
        
        # Itens
        self.pdf.set_font('Arial', '', 7)
        items = self.invoice.items.all()
        
        if not items.exists():
            self.pdf.cell(0, 5, 'Nenhum item cadastrado', 1, 1, 'C')
        else:
            for idx, item in enumerate(items, 1):
                self.pdf.cell(10, 5, str(idx), 1, 0, 'C')
                self.pdf.cell(60, 5, (item.description or '')[:35], 1, 0, 'L')
                self.pdf.cell(20, 5, item.ncm_code or '', 1, 0, 'C')
                self.pdf.cell(20, 5, f"{float(item.quantity or 0):.2f}", 1, 0, 'R')
                self.pdf.cell(15, 5, item.unit or '', 1, 0, 'C')
                self.pdf.cell(30, 5, self._format_currency(item.unit_price), 1, 0, 'R')
                self.pdf.cell(35, 5, self._format_currency(item.total_price), 1, 1, 'R')
        
        self.pdf.ln(2)
        
    def _build_totals(self):
        """Constrói totalizadores"""
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.cell(0, 5, 'CÁLCULO DO IMPOSTO', 1, 1, 'C')
        
        self.pdf.set_font('Arial', '', 8)
        totals = [
            ('Base ICMS', self._format_currency(self.invoice.icms_base)),
            ('Valor ICMS', self._format_currency(self.invoice.icms_value)),
            ('Base ICMS ST', 'R$ 0,00'),
            ('Valor ICMS ST', 'R$ 0,00'),
            ('Total Produtos', self._format_currency(self.invoice.total_products)),
            ('Valor Frete', self._format_currency(self.invoice.shipping)),
            ('Valor Seguro', self._format_currency(self.invoice.insurance)),
            ('Desconto', self._format_currency(self.invoice.discount)),
            ('Outras Despesas', self._format_currency(self.invoice.other_expenses)),
            ('Valor IPI', self._format_currency(self.invoice.ipi_value)),
            ('Valor Total', self._format_currency(self.invoice.total_value)),
        ]
        
        # 3 colunas
        col_width = 63
        row = 0
        for i, (label, value) in enumerate(totals):
            col = i % 3
            if col == 0 and i > 0:
                self.pdf.ln()
                row += 1
            self.pdf.cell(col_width, 5, f"{label}: {value}", 1, 0, 'L')
        
        self.pdf.ln()
        self.pdf.ln(2)
        
    def _build_transport(self):
        """Constrói dados de transporte"""
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.cell(0, 5, 'TRANSPORTADOR / VOLUMES TRANSPORTADOS', 1, 1, 'C')
        
        self.pdf.set_font('Arial', '', 8)
        freight_labels = {
            '0': '0-Emitente',
            '1': '1-Destinatário',
            '2': '2-Terceiros',
            '9': '9-Sem frete'
        }
        freight_mode = freight_labels.get(self.invoice.freight_mode, self.invoice.freight_mode or '')
        
        self.pdf.cell(95, 5, f"Modalidade do Frete: {freight_mode}", 1, 0)
        self.pdf.cell(95, 5, f"", 1, 1)
        
        self.pdf.ln(2)
        
    def _build_additional(self):
        """Constrói informações adicionais"""
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.cell(0, 5, 'DADOS ADICIONAIS', 1, 1, 'C')
        
        self.pdf.set_font('Arial', '', 7)
        notes = self.invoice.notes or 'Sem observações'
        
        # Quebra texto em linhas
        max_width = 190
        lines = []
        current_line = ''
        
        for word in notes.split():
            test_line = current_line + ' ' + word if current_line else word
            if self.pdf.get_string_width(test_line) < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for line in lines[:5]:  # Máximo 5 linhas
            self.pdf.cell(0, 4, line, 1, 1, 'L')
        
        # Preencher linhas vazias
        for _ in range(5 - len(lines)):
            self.pdf.cell(0, 4, '', 1, 1)
        
    def _build_footer(self):
        """Constrói rodapé"""
        self.pdf.ln(5)
        self.pdf.set_font('Arial', 'I', 7)
        self.pdf.cell(0, 5, 'Documento gerado eletronicamente - Contabiliza.IA', 0, 1, 'C')
        
        if self.invoice.access_key:
            # Formatar chave de acesso
            key = self.invoice.access_key
            formatted_key = ' '.join([key[i:i+4] for i in range(0, len(key), 4)])
            self.pdf.cell(0, 5, f"Chave de Acesso: {formatted_key}", 0, 1, 'C')
        
    def generate(self):
        """Gera o PDF completo e retorna bytes"""
        print("    [FPDF2] Construindo cabeçalho...")
        self._build_header()
        
        print("    [FPDF2] Construindo dados nota fiscal...")
        self._build_invoice_data()
        
        print("    [FPDF2] Construindo emitente/destinatário...")
        self._build_issuer_receiver()
        
        print("    [FPDF2] Construindo tabela de itens...")
        self._build_items_table()
        
        print("    [FPDF2] Construindo totalizadores...")
        self._build_totals()
        
        print("    [FPDF2] Construindo transporte...")
        self._build_transport()
        
        print("    [FPDF2] Construindo dados adicionais...")
        self._build_additional()
        
        print("    [FPDF2] Construindo rodapé...")
        self._build_footer()
        
        print("    [FPDF2] Gerando bytes do PDF...")
        # Retornar PDF como bytes
        return self.pdf.output()
