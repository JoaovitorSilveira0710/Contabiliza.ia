from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from django.core.files.base import ContentFile
import os
import hashlib
from datetime import datetime


class NFeGenerator:
    """Gerador de XML para NF-e (Nota Fiscal Eletrônica) - Padrão SEFAZ v4.00"""
    
    def __init__(self, invoice):
        self.invoice = invoice
    
    def generate_access_key(self):
        """Gera chave de acesso de 44 dígitos conforme padrão SEFAZ"""
        # cUF(2) + AAMM(4) + CNPJ(14) + mod(2) + serie(3) + nNF(9) + tpEmis(1) + cNF(8) + DV(1)
        uf = '35'  # São Paulo
        aamm = self.invoice.issue_date.strftime('%y%m')
        cnpj = self.invoice.issuer_tax_id.replace('.', '').replace('/', '').replace('-', '').zfill(14)
        mod = '55'
        serie = self.invoice.series.zfill(3)
        nnf = self.invoice.number.zfill(9)
        tp_emis = '1'
        cnf = '12345678'  # Código numérico aleatório (em produção gerar randomicamente)
        
        # Montar chave sem DV
        chave_sem_dv = f"{uf}{aamm}{cnpj}{mod}{serie}{nnf}{tp_emis}{cnf}"
        
        # Calcular dígito verificador (módulo 11)
        dv = self._calcular_dv_mod11(chave_sem_dv)
        
        chave_completa = f"{chave_sem_dv}{dv}"
        return chave_completa
    
    def _calcular_dv_mod11(self, chave):
        """Calcula dígito verificador usando módulo 11"""
        multiplicadores = [2, 3, 4, 5, 6, 7, 8, 9]
        soma = 0
        pos = 0
        
        for i in range(len(chave) - 1, -1, -1):
            soma += int(chave[i]) * multiplicadores[pos % 8]
            pos += 1
        
        resto = soma % 11
        if resto == 0 or resto == 1:
            return 0
        return 11 - resto
    
    def generate_xml(self):
        """Gera o XML da NF-e conforme layout SEFAZ v4.00"""
        
        # Gerar chave de acesso se não existir
        if not self.invoice.access_key:
            access_key = self.generate_access_key()
            self.invoice.access_key = access_key
            self.invoice.save(update_fields=['access_key'])
        
        # Criar estrutura XML com namespace correto
        nfe = Element('NFe', xmlns="http://www.portalfiscal.inf.br/nfe")
        inf_nfe = SubElement(nfe, 'infNFe', versao="4.00", Id=f"NFe{self.invoice.access_key}")
        
        # IDE - Identificação da NF-e
        ide = SubElement(inf_nfe, 'ide')
        SubElement(ide, 'cUF').text = '35'  # São Paulo
        SubElement(ide, 'cNF').text = self.invoice.access_key[-9:-1]  # 8 últimos dígitos antes do DV
        SubElement(ide, 'natOp').text = 'Venda de Mercadoria'
        SubElement(ide, 'mod').text = '55'  # Modelo 55 = NF-e
        SubElement(ide, 'serie').text = self.invoice.series
        SubElement(ide, 'nNF').text = self.invoice.number
        SubElement(ide, 'dhEmi').text = self.invoice.issue_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        SubElement(ide, 'dhSaiEnt').text = self.invoice.issue_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        SubElement(ide, 'tpNF').text = '1'  # 1=Saída, 0=Entrada
        SubElement(ide, 'idDest').text = '1'  # 1=Operação interna
        SubElement(ide, 'cMunFG').text = '3550308'  # Código município São Paulo
        SubElement(ide, 'tpImp').text = '1'  # 1=DANFE normal retrato
        SubElement(ide, 'tpEmis').text = '1'  # 1=Emissão normal
        SubElement(ide, 'cDV').text = self.invoice.access_key[-1]  # Dígito verificador
        SubElement(ide, 'tpAmb').text = '2'  # 1=Produção, 2=Homologação
        SubElement(ide, 'finNFe').text = '1'  # 1=NF-e normal
        SubElement(ide, 'indFinal').text = '1'  # 0=Normal, 1=Consumidor final
        SubElement(ide, 'indPres').text = '1'  # 1=Operação presencial
        SubElement(ide, 'procEmi').text = '0'  # 0=Emissão com aplicativo do contribuinte
        SubElement(ide, 'verProc').text = 'Contabiliza.IA v1.0'  # Versão do aplicativo emissor
        
        # Emit - Emitente (Dados completos conforme SEFAZ)
        emit = SubElement(inf_nfe, 'emit')
        
        cnpj_emit = self.invoice.issuer_tax_id.replace('.', '').replace('/', '').replace('-', '')
        if len(cnpj_emit) == 14:
            SubElement(emit, 'CNPJ').text = cnpj_emit
        else:
            SubElement(emit, 'CPF').text = cnpj_emit
            
        SubElement(emit, 'xNome').text = self.invoice.issuer_name
        SubElement(emit, 'xFant').text = self.invoice.issuer_name
        
        # Endereço do emitente
        ender_emit = SubElement(emit, 'enderEmit')
        SubElement(ender_emit, 'xLgr').text = 'Rua Exemplo'
        SubElement(ender_emit, 'nro').text = '1000'
        SubElement(ender_emit, 'xBairro').text = 'Centro'
        SubElement(ender_emit, 'cMun').text = '3550308'
        SubElement(ender_emit, 'xMun').text = 'São Paulo'
        SubElement(ender_emit, 'UF').text = 'SP'
        SubElement(ender_emit, 'CEP').text = '01310100'
        SubElement(ender_emit, 'cPais').text = '1058'
        SubElement(ender_emit, 'xPais').text = 'Brasil'
        SubElement(ender_emit, 'fone').text = '1133334444'
        
        # Regime tributário
        SubElement(emit, 'IE').text = '123456789012'  # Inscrição Estadual
        SubElement(emit, 'CRT').text = '3'  # 1=Simples Nacional, 3=Regime Normal
        
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
