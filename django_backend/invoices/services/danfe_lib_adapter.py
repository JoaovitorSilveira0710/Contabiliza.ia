from datetime import datetime
from pathlib import Path
from danfe import Danfe

class DanfeLibAdapter:
    """Adapter para gerar DANFE usando a biblioteca python-danfe a partir do nosso modelo Invoice."""
    def __init__(self, invoice):
        self.invoice = invoice

    def generate(self) -> bytes:
        inv = self.invoice
        d = Danfe()
        # Emissor
        d.emitente_nome = inv.issuer_name or ''
        d.emitente_logradouro = inv.issuer_address or ''
        d.emitente_numero = str(getattr(inv, 'issuer_number', '') or '')
        d.emitente_bairro = getattr(inv, 'issuer_district', '') or ''
        d.emitente_municipio = inv.issuer_city or ''
        d.emitente_uf = inv.issuer_state or ''
        d.emitente_cep = inv.issuer_zip_code or ''
        d.emitente_fone = inv.issuer_phone or ''
        d.emitente_ie = getattr(inv, 'issuer_state_registration', '') or ''
        # Destinatário
        d.destinatario_nome = inv.receiver_name or ''
        d.destinatario_cnpj = (inv.receiver_tax_id or '').replace('.', '').replace('-', '').replace('/', '')
        d.destinatario_logradouro = inv.receiver_address or ''
        d.destinatario_bairro = getattr(inv, 'receiver_district', '') or ''
        d.destinatario_municipio = inv.receiver_city or ''
        d.destinatario_uf = inv.receiver_state or ''
        d.destinatario_ie = getattr(inv, 'receiver_state_registration', '') or ''
        d.natureza_operacao = getattr(inv, 'operation_nature', 'Venda')
        # Nota
        d.numero_nota = str(inv.number or '')
        d.serie = str(inv.series or '')
        d.chave_nfe = inv.access_key or ''
        d.protocolo_autorizacao = inv.protocol or ''
        d.data_emissao = inv.issue_date or datetime.now()
        d.data_autorizacao = inv.authorization_date or inv.issue_date or datetime.now()
        # Valores
        d.valor_total_produtos = float(getattr(inv, 'total_products', 0) or 0)
        d.valor_total_nota = float(getattr(inv, 'total_value', 0) or 0)
        d.valor_frete = float(getattr(inv, 'shipping', 0) or 0)
        d.valor_seguro = float(getattr(inv, 'insurance', 0) or 0)
        d.valor_desconto = float(getattr(inv, 'discount', 0) or 0)
        d.outras_despesas = float(getattr(inv, 'other_expenses', 0) or 0)
        # Itens
        items_qs = getattr(inv, 'items', None)
        try:
            items = items_qs.all()
        except Exception:
            items = []
        for it in items:
            d.add_item(
                codigo=str(getattr(it, 'code', '') or ''),
                descricao=str(getattr(it, 'description', '') or ''),
                ncm=str(getattr(it, 'ncm', '') or ''),
                cfop=str(getattr(it, 'cfop', '') or ''),
                unidade=str(getattr(it, 'unit', '') or ''),
                quantidade=float(getattr(it, 'quantity', 0) or 0),
                valor_unitario=float(getattr(it, 'unit_value', 0) or 0),
                valor_total=float((getattr(it, 'quantity', 0) or 0) * (getattr(it, 'unit_value', 0) or 0)),
            )
        # Gerar bytes
        pdf_bytes = d.build_bytes()
        return pdf_bytes
