from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from django.core.files.base import ContentFile
from django.conf import settings
import os
import hashlib
from datetime import datetime


class NFeGenerator:
    """XML Generator for NF-e (Electronic Invoice) - SEFAZ-PR v4.00 Standard"""
    
    # UF IBGE Codes
    UF_CODES = {
        'AC': '12', 'AL': '27', 'AP': '16', 'AM': '13', 'BA': '29', 'CE': '23',
        'DF': '53', 'ES': '32', 'GO': '52', 'MA': '21', 'MT': '51', 'MS': '50',
        'MG': '31', 'PA': '15', 'PB': '25', 'PR': '41', 'PE': '26', 'PI': '22',
        'RJ': '33', 'RN': '24', 'RS': '43', 'RO': '11', 'RR': '14', 'SC': '42',
        'SE': '28', 'SP': '35', 'TO': '17'
    }
    
    def __init__(self, invoice):
        self.invoice = invoice
    
    def generate_access_key(self):
        """Generate 44-digit access key according to SEFAZ standard"""
        # cUF(2) + AAMM(4) + CNPJ/CPF(14) + mod(2) + serie(3) + nNF(9) + tpEmis(1) + cNF(8) + DV(1)
        
        # Use issuer's UF
        uf_code = self.UF_CODES.get(self.invoice.issuer_state or 'PR', '41')
        
        aamm = self.invoice.issue_date.strftime('%y%m')
        
        cnpj_cpf = self.invoice.issuer_tax_id.replace('.', '').replace('/', '').replace('-', '').strip()
        cnpj_cpf = cnpj_cpf.zfill(14)
        
        mod = self.invoice.model_code or '55'
        serie = str(self.invoice.series).zfill(3)
        nnf = str(self.invoice.number).zfill(9)
        tp_emis = '1'
        
        import random
        cnf = str(random.randint(10000000, 99999999))
        
        chave_sem_dv = f"{uf_code}{aamm}{cnpj_cpf}{mod}{serie}{nnf}{tp_emis}{cnf}"
        
        dv = self._calcular_dv_mod11(chave_sem_dv)
        
        chave_completa = f"{chave_sem_dv}{dv}"
        return chave_completa
    
    def _calcular_dv_mod11(self, chave):
        """Calculate check digit using module 11"""
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
    
    def _clean_tax_id(self, tax_id):
        """Remove formatação de CNPJ/CPF"""
        if not tax_id:
            return ''
        return tax_id.replace('.', '').replace('/', '').replace('-', '').strip()
    
    def _format_decimal(self, value, decimals=2):
        """Formata valor decimal para string com casas decimais fixas"""
        if value is None:
            value = 0
        return f"{float(value):.{decimals}f}"
    
    def generate_xml(self):
        """Gera o XML da NF-e conforme layout SEFAZ-PR v4.00"""
        
        # Gerar chave de acesso se não existir
        if not self.invoice.access_key:
            access_key = self.generate_access_key()
            self.invoice.access_key = access_key
            self.invoice.save(update_fields=['access_key'])
        
        # Criar estrutura XML com namespace correto
        nfe = Element('NFe', xmlns="http://www.portalfiscal.inf.br/nfe")
        inf_nfe = SubElement(nfe, 'infNFe', versao="4.00", Id=f"NFe{self.invoice.access_key}")
        
        # ========== IDE - Identificação da NF-e ==========
        ide = SubElement(inf_nfe, 'ide')
        
        # UF do emitente
        uf_code = self.UF_CODES.get(self.invoice.issuer_state or 'PR', '41')
        SubElement(ide, 'cUF').text = uf_code
        
        # Código numérico (8 dígitos antes do DV)
        SubElement(ide, 'cNF').text = self.invoice.access_key[-9:-1]
        
        # Natureza da operação
        nat_op_map = {
            'venda_producao': 'Venda de producao',
            'venda_mercadoria': 'Venda',
            'venda_soja': 'Venda',
            'prestacao_servico': 'Prestacao de servico',
            'devolucao': 'Devolucao',
            'transferencia': 'Transferencia',
            'remessa': 'Remessa',
            'outras': 'Venda',
        }
        nat_op = nat_op_map.get(self.invoice.operation_nature, 'Venda')
        SubElement(ide, 'natOp').text = nat_op
        
        SubElement(ide, 'mod').text = self.invoice.model_code or '55'
        SubElement(ide, 'serie').text = str(self.invoice.series)
        SubElement(ide, 'nNF').text = str(self.invoice.number)
        SubElement(ide, 'dhEmi').text = self.invoice.issue_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        SubElement(ide, 'dhSaiEnt').text = self.invoice.issue_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        # Tipo de operação: 0=Entrada, 1=Saída
        tp_nf = '1' if self.invoice.operation_type == 'saida' else '0'
        SubElement(ide, 'tpNF').text = tp_nf
        
        # Indicador de destino da operação
        id_dest = getattr(self.invoice, 'destination_indicator', '1')
        SubElement(ide, 'idDest').text = id_dest
        
        # Código município IBGE do emitente
        c_mun_fg = self.invoice.issuer_city_code or '4104428'  # Default Candoi-PR
        SubElement(ide, 'cMunFG').text = c_mun_fg
        
        SubElement(ide, 'tpImp').text = '1'  # 1=DANFE retrato
        SubElement(ide, 'tpEmis').text = '1'  # 1=Emissão normal
        SubElement(ide, 'cDV').text = self.invoice.access_key[-1]
        
        # Ambiente: 1=Produção, 2=Homologação
        tp_amb = getattr(self.invoice, 'environment', '2')
        SubElement(ide, 'tpAmb').text = tp_amb
        
        SubElement(ide, 'finNFe').text = '1'  # 1=NF-e normal
        
        # Indicador consumidor final
        ind_final = getattr(self.invoice, 'final_consumer_indicator', '0')
        SubElement(ide, 'indFinal').text = ind_final
        
        # Indicador de presença
        ind_pres = getattr(self.invoice, 'presence_indicator', '0')
        SubElement(ide, 'indPres').text = ind_pres
        
        # Processo de emissão: 0=App contribuinte, 1=Avulsa Fisco, 2=Avulsa contrib, 3=Contrib site
        SubElement(ide, 'procEmi').text = '0'
        SubElement(ide, 'verProc').text = 'Contabiliza.IA v1.0'
        
        # ========== EMIT - Emitente ==========
        emit = SubElement(inf_nfe, 'emit')
        
        cnpj_emit = self._clean_tax_id(self.invoice.issuer_tax_id)
        if len(cnpj_emit) == 14:
            SubElement(emit, 'CNPJ').text = cnpj_emit
        elif len(cnpj_emit) == 11:
            SubElement(emit, 'CPF').text = cnpj_emit
        
        SubElement(emit, 'xNome').text = self.invoice.issuer_name or 'EMITENTE'
        
        if self.invoice.issuer_fantasy_name:
            SubElement(emit, 'xFant').text = self.invoice.issuer_fantasy_name
        
        # Endereço do emitente
        ender_emit = SubElement(emit, 'enderEmit')
        SubElement(ender_emit, 'xLgr').text = self.invoice.issuer_address or 'Rua'
        SubElement(ender_emit, 'nro').text = self.invoice.issuer_number or 'S/N'
        SubElement(ender_emit, 'xBairro').text = self.invoice.issuer_district or 'Centro'
        SubElement(ender_emit, 'cMun').text = c_mun_fg
        SubElement(ender_emit, 'xMun').text = self.invoice.issuer_city or 'Municipio'
        SubElement(ender_emit, 'UF').text = self.invoice.issuer_state or 'PR'
        
        cep_emit = self._clean_tax_id(self.invoice.issuer_zip_code or '85140000')
        SubElement(ender_emit, 'CEP').text = cep_emit
        
        SubElement(ender_emit, 'cPais').text = '1058'
        SubElement(ender_emit, 'xPais').text = 'BRASIL'
        
        if self.invoice.issuer_phone:
            phone_emit = self._clean_tax_id(self.invoice.issuer_phone)
            SubElement(ender_emit, 'fone').text = phone_emit
        
        # IE e CRT
        if self.invoice.issuer_state_registration:
            SubElement(emit, 'IE').text = self.invoice.issuer_state_registration
        
        # CRT - Código Regime Tributário
        crt = getattr(self.invoice, 'tax_regime', '3')
        SubElement(emit, 'CRT').text = crt
        
        # ========== DEST - Destinatário ==========
        dest = SubElement(inf_nfe, 'dest')
        client = self.invoice.client
        
        cnpj_dest = self._clean_tax_id(client.tax_id)
        if len(cnpj_dest) == 14:
            SubElement(dest, 'CNPJ').text = cnpj_dest
        elif len(cnpj_dest) == 11:
            SubElement(dest, 'CPF').text = cnpj_dest
        
        SubElement(dest, 'xNome').text = client.name
        
        # Endereço do destinatário
        ender_dest = SubElement(dest, 'enderDest')
        SubElement(ender_dest, 'xLgr').text = client.street or 'Rua'
        SubElement(ender_dest, 'nro').text = client.number or 'S/N'
        
        if client.complement:
            SubElement(ender_dest, 'xCpl').text = client.complement
        
        SubElement(ender_dest, 'xBairro').text = client.neighborhood or 'Centro'
        
        # Código município destinatário
        c_mun_dest = self.invoice.receiver_city_code or '4109401'
        SubElement(ender_dest, 'cMun').text = c_mun_dest
        SubElement(ender_dest, 'xMun').text = client.city or 'Municipio'
        SubElement(ender_dest, 'UF').text = client.state or 'PR'
        
        cep_dest = self._clean_tax_id(client.zip_code or '85000000')
        SubElement(ender_dest, 'CEP').text = cep_dest
        
        SubElement(ender_dest, 'cPais').text = '1058'
        SubElement(ender_dest, 'xPais').text = 'BRASIL'
        
        # Indicador IE destinatário: 1=Contribuinte, 2=Isento, 9=Não contribuinte
        ind_ie_dest = getattr(self.invoice, 'receiver_ie_indicator', '9')
        SubElement(dest, 'indIEDest').text = ind_ie_dest
        
        if client.state_registration and ind_ie_dest == '1':
            SubElement(dest, 'IE').text = client.state_registration
        
        # ========== DET - Itens/Produtos ==========
        for idx, item in enumerate(self.invoice.items.all(), 1):
            det = SubElement(inf_nfe, 'det', nItem=str(idx))
            
            # Produto
            prod = SubElement(det, 'prod')
            SubElement(prod, 'cProd').text = item.code or str(idx)
            SubElement(prod, 'cEAN').text = 'SEM GTIN'
            SubElement(prod, 'xProd').text = item.description
            
            if item.ncm:
                SubElement(prod, 'NCM').text = item.ncm
            
            SubElement(prod, 'CFOP').text = item.cfop or '5101'
            SubElement(prod, 'uCom').text = item.unit or 'UN'
            SubElement(prod, 'qCom').text = self._format_decimal(item.quantity, 4)
            SubElement(prod, 'vUnCom').text = self._format_decimal(item.unit_value, 10)
            SubElement(prod, 'vProd').text = self._format_decimal(item.total_value, 2)
            
            SubElement(prod, 'cEANTrib').text = 'SEM GTIN'
            SubElement(prod, 'uTrib').text = item.unit or 'UN'
            SubElement(prod, 'qTrib').text = self._format_decimal(item.quantity, 4)
            SubElement(prod, 'vUnTrib').text = self._format_decimal(item.unit_value, 10)
            SubElement(prod, 'indTot').text = '1'  # 1=Compõe total da NF-e
            
            # Impostos
            imposto = SubElement(det, 'imposto')
            
            # ICMS
            icms = SubElement(imposto, 'ICMS')
            
            # Ler CST do item (se existir o campo)
            icms_cst = getattr(item, 'icms_cst', '00')
            icms_orig = getattr(item, 'icms_origin', '0')
            
            # Criar tag ICMS conforme CST
            if icms_cst in ['00', '10', '20', '30', '40', '41', '50', '51', '60', '70', '90']:
                icms_tag = SubElement(icms, f'ICMS{icms_cst}')
                SubElement(icms_tag, 'orig').text = icms_orig
                SubElement(icms_tag, 'CST').text = icms_cst
                
                # Campos específicos conforme CST
                if icms_cst == '00':  # Tributado integralmente
                    SubElement(icms_tag, 'vBC').text = self._format_decimal(item.total_value, 2)
                    SubElement(icms_tag, 'pICMS').text = self._format_decimal(item.icms_rate, 2)
                    SubElement(icms_tag, 'vICMS').text = self._format_decimal(item.icms_value, 2)
                # CST 90 - Outros (não precisa de vBC/pICMS/vICMS obrigatórios)
            else:
                # Default para ICMS90
                icms90 = SubElement(icms, 'ICMS90')
                SubElement(icms90, 'orig').text = icms_orig
                SubElement(icms90, 'CST').text = '90'
            
            # PIS
            pis = SubElement(imposto, 'PIS')
            pis_cst = getattr(item, 'pis_cst', '01')
            
            if pis_cst in ['04', '05', '06', '07', '08', '09']:
                # PIS Não Tributado
                pis_nt = SubElement(pis, 'PISNT')
                SubElement(pis_nt, 'CST').text = pis_cst
            else:
                # PIS com alíquota
                pis_aliq = SubElement(pis, 'PISAliq')
                SubElement(pis_aliq, 'CST').text = pis_cst
                SubElement(pis_aliq, 'vBC').text = self._format_decimal(item.total_value, 2)
                SubElement(pis_aliq, 'pPIS').text = self._format_decimal(item.pis_rate, 4)
                SubElement(pis_aliq, 'vPIS').text = self._format_decimal(item.pis_value, 2)
            
            # COFINS
            cofins = SubElement(imposto, 'COFINS')
            cofins_cst = getattr(item, 'cofins_cst', '01')
            
            if cofins_cst in ['04', '05', '06', '07', '08', '09']:
                # COFINS Não Tributado
                cofins_nt = SubElement(cofins, 'COFINSNT')
                SubElement(cofins_nt, 'CST').text = cofins_cst
            else:
                # COFINS com alíquota
                cofins_aliq = SubElement(cofins, 'COFINSAliq')
                SubElement(cofins_aliq, 'CST').text = cofins_cst
                SubElement(cofins_aliq, 'vBC').text = self._format_decimal(item.total_value, 2)
                SubElement(cofins_aliq, 'pCOFINS').text = self._format_decimal(item.cofins_rate, 4)
                SubElement(cofins_aliq, 'vCOFINS').text = self._format_decimal(item.cofins_value, 2)
        
        # ========== TOTAL - Totalizadores ==========
        total = SubElement(inf_nfe, 'total')
        icms_tot = SubElement(total, 'ICMSTot')
        
        SubElement(icms_tot, 'vBC').text = self._format_decimal(self.invoice.icms_base, 2)
        SubElement(icms_tot, 'vICMS').text = self._format_decimal(self.invoice.icms_value, 2)
        SubElement(icms_tot, 'vICMSDeson').text = '0.00'
        
        # Campos partilha ICMS (operações interestaduais consumidor final)
        SubElement(icms_tot, 'vFCPUFDest').text = '0.00'
        SubElement(icms_tot, 'vICMSUFDest').text = '0.00'
        SubElement(icms_tot, 'vICMSUFRemet').text = '0.00'
        
        SubElement(icms_tot, 'vFCP').text = '0.00'
        SubElement(icms_tot, 'vBCST').text = '0.00'
        SubElement(icms_tot, 'vST').text = '0.00'
        SubElement(icms_tot, 'vFCPST').text = '0.00'
        SubElement(icms_tot, 'vFCPSTRet').text = '0.00'
        
        SubElement(icms_tot, 'vProd').text = self._format_decimal(self.invoice.total_products, 2)
        SubElement(icms_tot, 'vFrete').text = self._format_decimal(self.invoice.shipping, 2)
        SubElement(icms_tot, 'vSeg').text = self._format_decimal(self.invoice.insurance, 2)
        SubElement(icms_tot, 'vDesc').text = self._format_decimal(self.invoice.discount, 2)
        
        SubElement(icms_tot, 'vII').text = '0.00'
        SubElement(icms_tot, 'vIPI').text = self._format_decimal(self.invoice.ipi_value, 2)
        SubElement(icms_tot, 'vIPIDevol').text = '0.00'
        
        SubElement(icms_tot, 'vPIS').text = self._format_decimal(self.invoice.pis_value, 2)
        SubElement(icms_tot, 'vCOFINS').text = self._format_decimal(self.invoice.cofins_value, 2)
        
        SubElement(icms_tot, 'vOutro').text = self._format_decimal(self.invoice.other_expenses, 2)
        SubElement(icms_tot, 'vNF').text = self._format_decimal(self.invoice.total_value, 2)
        
        # ========== TRANSP - Transporte ==========
        transp = SubElement(inf_nfe, 'transp')
        
        # Modalidade do frete
        mod_frete = getattr(self.invoice, 'freight_mode', '9')
        SubElement(transp, 'modFrete').text = mod_frete
        
        # ========== PAG - Pagamento (obrigatório v4.00) ==========
        pag = SubElement(inf_nfe, 'pag')
        det_pag = SubElement(pag, 'detPag')
        
        # Indicador pagamento: 0=À vista, 1=À prazo
        ind_pag = getattr(self.invoice, 'payment_indicator', '0')
        SubElement(det_pag, 'indPag').text = ind_pag
        
        # Meio de pagamento
        t_pag = getattr(self.invoice, 'payment_method', '99')
        SubElement(det_pag, 'tPag').text = t_pag
        
        # Descrição do pagamento (opcional, mas recomendado para tPag=99)
        if hasattr(self.invoice, 'payment_description') and self.invoice.payment_description:
            SubElement(det_pag, 'xPag').text = self.invoice.payment_description
        
        SubElement(det_pag, 'vPag').text = self._format_decimal(self.invoice.total_value, 2)
        
        # ========== INFADIC - Informações Adicionais ==========
        if self.invoice.additional_info or self.invoice.notes:
            inf_adic = SubElement(inf_nfe, 'infAdic')
            
            info_text = []
            if self.invoice.notes:
                info_text.append(self.invoice.notes)
            if self.invoice.additional_info:
                info_text.append(self.invoice.additional_info)
            
            SubElement(inf_adic, 'infCpl').text = ' | '.join(info_text)
        
        # ========== INFRESPTEC - Responsável Técnico (opcional) ==========
        if hasattr(self.invoice, 'tech_cnpj') and self.invoice.tech_cnpj:
            inf_resp_tec = SubElement(inf_nfe, 'infRespTec')
            SubElement(inf_resp_tec, 'CNPJ').text = self._clean_tax_id(self.invoice.tech_cnpj)
            
            if hasattr(self.invoice, 'tech_contact') and self.invoice.tech_contact:
                SubElement(inf_resp_tec, 'xContato').text = self.invoice.tech_contact
            
            if hasattr(self.invoice, 'tech_email') and self.invoice.tech_email:
                SubElement(inf_resp_tec, 'email').text = self.invoice.tech_email
            
            if hasattr(self.invoice, 'tech_phone') and self.invoice.tech_phone:
                SubElement(inf_resp_tec, 'fone').text = self._clean_tax_id(self.invoice.tech_phone)
        
        # Formatar XML
        xml_string = minidom.parseString(tostring(nfe, encoding='utf-8')).toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
        
        # Remover declaração XML duplicada se existir
        if xml_string.count('<?xml') > 1:
            lines = xml_string.split('\n')
            xml_string = '\n'.join([line for i, line in enumerate(lines) if not (i > 0 and '<?xml' in line)])
        
        # Salvar arquivo
        filename = f"NFe{self.invoice.number}_{self.invoice.series}.xml"
        self.invoice.xml_file.save(filename, ContentFile(xml_string.encode('utf-8')), save=False)
        self.invoice.save(update_fields=['xml_file'])
        
        return xml_string
    
    def validate_xml(self, xml_string):
        """Validar XML contra schema XSD da SEFAZ"""
        try:
            from lxml import etree
            
            # Caminho para XSD (deve ser baixado da SEFAZ)
            xsd_path = os.path.join(settings.BASE_DIR, 'static', 'xsd', 'nfe_v4.00.xsd')
            
            if not os.path.exists(xsd_path):
                print(f"Aviso: XSD não encontrado em {xsd_path}. Validação pulada.")
                return True
            
            # Parse XSD
            with open(xsd_path, 'rb') as xsd_file:
                xsd_doc = etree.parse(xsd_file)
                xsd_schema = etree.XMLSchema(xsd_doc)
            
            # Parse XML
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            # Validar
            is_valid = xsd_schema.validate(xml_doc)
            
            if not is_valid:
                errors = xsd_schema.error_log
                print(f"Erros de validação XML:\n{errors}")
                return False
            
            return True
            
        except ImportError:
            print("Aviso: lxml não instalado. Instale com: pip install lxml")
            return True
        except Exception as e:
            print(f"Erro na validação: {e}")
            return False
