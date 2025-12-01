from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from django.core.files.base import ContentFile
import os


class NFeGenerator:
    """Gerador de XML para NF-e (Nota Fiscal Eletrônica)"""
    
    def __init__(self, invoice):
        self.invoice = invoice
    
    def generate_xml(self):
        """Gera o XML da NF-e"""
        # Criar estrutura XML
        nfe = Element('NFe', xmlns="http://www.portalfiscal.inf.br/nfe")
        inf_nfe = SubElement(nfe, 'infNFe', versao="4.00", Id=f"NFe{self.invoice.access_key}")
        
        # IDE - Identificação
        ide = SubElement(inf_nfe, 'ide')
        SubElement(ide, 'cUF').text = '35'  # São Paulo
        SubElement(ide, 'cNF').text = self.invoice.number.zfill(8)
        SubElement(ide, 'natOp').text = 'Venda de Mercadoria'
        SubElement(ide, 'mod').text = '55'  # Modelo 55 = NF-e
        SubElement(ide, 'serie').text = self.invoice.series
        SubElement(ide, 'nNF').text = self.invoice.number
        SubElement(ide, 'dhEmi').text = self.invoice.issue_date.isoformat()
        SubElement(ide, 'tpNF').text = '1'  # 1=Saída
        SubElement(ide, 'idDest').text = '1'  # 1=Operação interna
        SubElement(ide, 'tpImp').text = '1'  # 1=DANFE normal
        SubElement(ide, 'tpEmis').text = '1'  # 1=Emissão normal
        SubElement(ide, 'tpAmb').text = '2'  # 2=Homologação
        SubElement(ide, 'finNFe').text = '1'  # 1=NF-e normal
        SubElement(ide, 'indFinal').text = '1'  # 1=Consumidor final
        SubElement(ide, 'indPres').text = '1'  # 1=Operação presencial
        
        # Emit - Emitente
        emit = SubElement(inf_nfe, 'emit')
        SubElement(emit, 'CNPJ').text = self.invoice.issuer_tax_id.replace('.', '').replace('/', '').replace('-', '')
        SubElement(emit, 'xNome').text = self.invoice.issuer_name
        SubElement(emit, 'xFant').text = self.invoice.issuer_name
        
        # Dest - Destinatário
        dest = SubElement(inf_nfe, 'dest')
        client = self.invoice.client
        
        if client.person_type == 'PF':
            SubElement(dest, 'CPF').text = client.tax_id.replace('.', '').replace('-', '')
        else:
            SubElement(dest, 'CNPJ').text = client.tax_id.replace('.', '').replace('/', '').replace('-', '')
        
        SubElement(dest, 'xNome').text = client.name
        
        # Endereço do destinatário
        ender_dest = SubElement(dest, 'enderDest')
        SubElement(ender_dest, 'xLgr').text = client.street
        SubElement(ender_dest, 'nro').text = client.number
        if client.complement:
            SubElement(ender_dest, 'xCpl').text = client.complement
        SubElement(ender_dest, 'xBairro').text = client.neighborhood
        SubElement(ender_dest, 'cMun').text = '3550308'  # Código São Paulo
        SubElement(ender_dest, 'xMun').text = client.city
        SubElement(ender_dest, 'UF').text = client.state
        SubElement(ender_dest, 'CEP').text = client.zip_code.replace('-', '')
        SubElement(ender_dest, 'cPais').text = '1058'
        SubElement(ender_dest, 'xPais').text = 'Brasil'
        
        # Itens
        for idx, item in enumerate(self.invoice.items.all(), 1):
            det = SubElement(inf_nfe, 'det', nItem=str(idx))
            
            # Produto
            prod = SubElement(det, 'prod')
            SubElement(prod, 'cProd').text = item.code
            SubElement(prod, 'cEAN').text = 'SEM GTIN'
            SubElement(prod, 'xProd').text = item.description
            if item.ncm:
                SubElement(prod, 'NCM').text = item.ncm
            SubElement(prod, 'CFOP').text = item.cfop
            SubElement(prod, 'uCom').text = item.unit
            SubElement(prod, 'qCom').text = str(item.quantity)
            SubElement(prod, 'vUnCom').text = f"{item.unit_value:.2f}"
            SubElement(prod, 'vProd').text = f"{item.total_value:.2f}"
            SubElement(prod, 'cEANTrib').text = 'SEM GTIN'
            SubElement(prod, 'uTrib').text = item.unit
            SubElement(prod, 'qTrib').text = str(item.quantity)
            SubElement(prod, 'vUnTrib').text = f"{item.unit_value:.2f}"
            SubElement(prod, 'indTot').text = '1'
            
            # Impostos
            imposto = SubElement(det, 'imposto')
            
            # ICMS
            icms = SubElement(imposto, 'ICMS')
            icms00 = SubElement(icms, 'ICMS00')
            SubElement(icms00, 'orig').text = '0'
            SubElement(icms00, 'CST').text = '00'
            SubElement(icms00, 'vBC').text = f"{item.total_value:.2f}"
            SubElement(icms00, 'pICMS').text = f"{item.icms_rate:.2f}"
            SubElement(icms00, 'vICMS').text = f"{item.icms_value:.2f}"
            
            # PIS
            pis = SubElement(imposto, 'PIS')
            pis_aliq = SubElement(pis, 'PISAliq')
            SubElement(pis_aliq, 'CST').text = '01'
            SubElement(pis_aliq, 'vBC').text = f"{item.total_value:.2f}"
            SubElement(pis_aliq, 'pPIS').text = f"{item.pis_rate:.2f}"
            SubElement(pis_aliq, 'vPIS').text = f"{item.pis_value:.2f}"
            
            # COFINS
            cofins = SubElement(imposto, 'COFINS')
            cofins_aliq = SubElement(cofins, 'COFINSAliq')
            SubElement(cofins_aliq, 'CST').text = '01'
            SubElement(cofins_aliq, 'vBC').text = f"{item.total_value:.2f}"
            SubElement(cofins_aliq, 'pCOFINS').text = f"{item.cofins_rate:.2f}"
            SubElement(cofins_aliq, 'vCOFINS').text = f"{item.cofins_value:.2f}"
        
        # Total
        total = SubElement(inf_nfe, 'total')
        icms_tot = SubElement(total, 'ICMSTot')
        SubElement(icms_tot, 'vBC').text = f"{self.invoice.icms_base:.2f}"
        SubElement(icms_tot, 'vICMS').text = f"{self.invoice.icms_value:.2f}"
        SubElement(icms_tot, 'vICMSDeson').text = '0.00'
        SubElement(icms_tot, 'vFCP').text = '0.00'
        SubElement(icms_tot, 'vBCST').text = '0.00'
        SubElement(icms_tot, 'vST').text = '0.00'
        SubElement(icms_tot, 'vFCPST').text = '0.00'
        SubElement(icms_tot, 'vFCPSTRet').text = '0.00'
        SubElement(icms_tot, 'vProd').text = f"{self.invoice.total_products:.2f}"
        SubElement(icms_tot, 'vFrete').text = f"{self.invoice.shipping:.2f}"
        SubElement(icms_tot, 'vSeg').text = f"{self.invoice.insurance:.2f}"
        SubElement(icms_tot, 'vDesc').text = f"{self.invoice.discount:.2f}"
        SubElement(icms_tot, 'vII').text = '0.00'
        SubElement(icms_tot, 'vIPI').text = f"{self.invoice.ipi_value:.2f}"
        SubElement(icms_tot, 'vIPIDevol').text = '0.00'
        SubElement(icms_tot, 'vPIS').text = f"{self.invoice.pis_value:.2f}"
        SubElement(icms_tot, 'vCOFINS').text = f"{self.invoice.cofins_value:.2f}"
        SubElement(icms_tot, 'vOutro').text = f"{self.invoice.other_expenses:.2f}"
        SubElement(icms_tot, 'vNF').text = f"{self.invoice.total_value:.2f}"
        
        # Informações Adicionais
        if self.invoice.additional_info or self.invoice.notes:
            inf_adic = SubElement(inf_nfe, 'infAdic')
            if self.invoice.notes:
                SubElement(inf_adic, 'infCpl').text = self.invoice.notes
        
        # Formatar XML
        xml_string = minidom.parseString(tostring(nfe)).toprettyxml(indent="  ")
        
        # Salvar arquivo
        filename = f"NFe{self.invoice.number}_{self.invoice.series}.xml"
        self.invoice.xml_file.save(filename, ContentFile(xml_string.encode('utf-8')))
        
        return xml_string
    
    def validate_xml(self, xml_string):
        """Validar XML contra schema XSD (implementação simplificada)"""
        # Em produção, usar lxml para validar contra XSD oficial da SEFAZ
        return True
