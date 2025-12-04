"""
Gerador de XML de NF-e no padrão SEFAZ v4.00
Gera XML completo conforme schema da Receita Federal
"""
from lxml import etree
from datetime import datetime
import hashlib
import re


class NFeXMLGenerator:
    """Gera XML de NF-e no padrão SEFAZ v4.00"""
    
    NAMESPACE = "http://www.portalfiscal.inf.br/nfe"
    
    def __init__(self, invoice):
        """
        Inicializa o gerador com uma Invoice
        
        Args:
            invoice: Objeto Invoice do Django
        """
        self.invoice = invoice
        self.nsmap = {None: self.NAMESPACE}
    
    def generate(self):
        """
        Gera o XML completo da NF-e
        
        Returns:
            str: XML da NF-e formatado
        """
        # Criar elemento raiz
        nfe = etree.Element("NFe", nsmap=self.nsmap, versao="4.00")
        
        # Gerar infNFe (informações da NF-e)
        inf_nfe = self._generate_inf_nfe()
        nfe.append(inf_nfe)
        
        # Converter para string
        xml_string = etree.tostring(
            nfe,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')
        
        return xml_string
    
    def _generate_inf_nfe(self):
        """Gera a tag infNFe com todas as informações"""
        # Gerar chave de acesso
        chave_acesso = self._generate_chave_acesso()
        
        inf_nfe = etree.Element("infNFe", versao="4.00", Id=f"NFe{chave_acesso}")
        
        # 1. Identificação da NF-e (ide)
        inf_nfe.append(self._generate_ide())
        
        # 2. Emitente (emit)
        inf_nfe.append(self._generate_emit())
        
        # 3. Destinatário (dest)
        if self.invoice.client:
            inf_nfe.append(self._generate_dest())
        
        # 4. Itens da NF-e (det)
        for idx, item in enumerate(self.invoice.items.all(), start=1):
            inf_nfe.append(self._generate_det(item, idx))
        
        # 5. Total da NF-e (total)
        inf_nfe.append(self._generate_total())
        
        # 6. Transporte (transp)
        inf_nfe.append(self._generate_transp())
        
        # 7. Cobrança (cobr) - opcional
        if self.invoice.payment_method and self.invoice.payment_indicator == '1':
            inf_nfe.append(self._generate_cobr())
        
        # 8. Pagamento (pag)
        inf_nfe.append(self._generate_pag())
        
        # 9. Informações Adicionais (infAdic) - opcional
        if self.invoice.additional_info or self.invoice.notes:
            inf_nfe.append(self._generate_inf_adic())
        
        return inf_nfe
    
    def _generate_ide(self):
        """Gera identificação da NF-e"""
        ide = etree.Element("ide")
        
        # Código UF
        self._add_element(ide, "cUF", self._get_uf_code(self.invoice.issuer_state))
        
        # Código numérico (8 dígitos aleatórios)
        self._add_element(ide, "cNF", str(self.invoice.id).zfill(8)[-8:])
        
        # Natureza da operação
        nature_map = {
            'venda_producao': 'VENDA DE PRODUCAO DO ESTABELECIMENTO',
            'venda_mercadoria': 'VENDA DE MERCADORIA ADQUIRIDA/RECEBIDA DE TERCEIROS',
            'venda_soja': 'VENDA DE SOJA',
            'prestacao_servico': 'PRESTACAO DE SERVICO',
            'devolucao': 'DEVOLUCAO DE MERCADORIA',
            'transferencia': 'TRANSFERENCIA',
            'remessa': 'REMESSA',
            'outras': 'OUTRAS'
        }
        nat_op = nature_map.get(self.invoice.operation_nature, 'VENDA DE PRODUCAO')
        self._add_element(ide, "natOp", nat_op)
        
        # Modelo do documento fiscal (55 = NF-e)
        self._add_element(ide, "mod", "55")
        
        # Série
        self._add_element(ide, "serie", str(self.invoice.series or "1"))
        
        # Número da NF-e
        self._add_element(ide, "nNF", str(self.invoice.number))
        
        # Data e hora de emissão
        dt_emissao = self.invoice.issue_date or datetime.now()
        self._add_element(ide, "dhEmi", dt_emissao.strftime("%Y-%m-%dT%H:%M:%S-03:00"))
        
        # Data e hora de saída (se houver)
        if self.invoice.authorization_date:
            self._add_element(ide, "dhSaiEnt", self.invoice.authorization_date.strftime("%Y-%m-%dT%H:%M:%S-03:00"))
        
        # Tipo de operação (0=Entrada, 1=Saída)
        tp_nf = "1" if self.invoice.operation_type == 'saida' else "0"
        self._add_element(ide, "tpNF", tp_nf)
        
        # Identificador de local de destino
        # 1=Operação interna, 2=Interestadual, 3=Exterior
        id_dest = self.invoice.destination_indicator or "1"
        self._add_element(ide, "idDest", id_dest)
        
        # Código do município de ocorrência do fato gerador
        self._add_element(ide, "cMunFG", str(self.invoice.issuer_city_code or "4106902"))
        
        # Formato de impressão do DANFE (1=Retrato, 2=Paisagem)
        self._add_element(ide, "tpImp", "1")
        
        # Tipo de emissão (1=Normal)
        self._add_element(ide, "tpEmis", "1")
        
        # Dígito verificador da chave de acesso
        chave = self._generate_chave_acesso()
        self._add_element(ide, "cDV", chave[-1])
        
        # Tipo de ambiente (1=Produção, 2=Homologação)
        ambiente = self.invoice.environment or '2'
        self._add_element(ide, "tpAmb", str(ambiente))
        
        # Finalidade da emissão (1=Normal, 2=Complementar, 3=Ajuste, 4=Devolução)
        self._add_element(ide, "finNFe", "1")
        
        # Indica se é consumidor final (0=Não, 1=Sim)
        ind_final = self.invoice.final_consumer_indicator or '1'
        self._add_element(ide, "indFinal", ind_final)
        
        # Indicador de presença (1=Presencial, 2=Internet, 9=Não se aplica)
        ind_pres = self.invoice.presence_indicator or '1'
        self._add_element(ide, "indPres", ind_pres)
        
        # Processo de emissão (0=Aplicativo do contribuinte)
        self._add_element(ide, "procEmi", "0")
        
        # Versão do processo de emissão
        self._add_element(ide, "verProc", "1.0.0")
        
        return ide
    
    def _generate_emit(self):
        """Gera dados do emitente"""
        emit = etree.Element("emit")
        
        # CNPJ ou CPF
        issuer_tax_id = re.sub(r'\D', '', self.invoice.issuer_tax_id or '')
        if len(issuer_tax_id) == 14:
            self._add_element(emit, "CNPJ", issuer_tax_id)
        else:
            self._add_element(emit, "CPF", issuer_tax_id)
        
        # Nome/Razão Social
        self._add_element(emit, "xNome", self.invoice.issuer_name or "")
        
        # Endereço
        ender_emit = etree.SubElement(emit, "enderEmit")
        self._add_element(ender_emit, "xLgr", self.invoice.issuer_address or "")
        self._add_element(ender_emit, "nro", self.invoice.issuer_number or "S/N")
        if hasattr(self.invoice, 'issuer_complement') and self.invoice.issuer_complement:
            self._add_element(ender_emit, "xCpl", self.invoice.issuer_complement)
        # Usar issuer_district se existir, senão ignorar
        bairro = getattr(self.invoice, 'issuer_district', '') or getattr(self.invoice, 'issuer_neighborhood', '') or ''
        self._add_element(ender_emit, "xBairro", bairro)
        self._add_element(ender_emit, "cMun", str(self.invoice.issuer_city_code or "4106902"))
        self._add_element(ender_emit, "xMun", self.invoice.issuer_city or "")
        self._add_element(ender_emit, "UF", self.invoice.issuer_state or "PR")
        cep = re.sub(r'\D', '', self.invoice.issuer_zip_code or '')
        self._add_element(ender_emit, "CEP", cep)
        self._add_element(ender_emit, "cPais", "1058")  # Brasil
        self._add_element(ender_emit, "xPais", "Brasil")
        if self.invoice.issuer_phone:
            phone = re.sub(r'\D', '', self.invoice.issuer_phone)
            self._add_element(ender_emit, "fone", phone)
        
        # Inscrição Estadual
        if self.invoice.issuer_state_registration:
            ie = re.sub(r'\D', '', self.invoice.issuer_state_registration)
            self._add_element(emit, "IE", ie)
        
        # Regime Tributário (1=Simples Nacional, 3=Normal)
        crt = self.invoice.tax_regime or '3'
        self._add_element(emit, "CRT", str(crt))
        
        return emit
    
    def _generate_dest(self):
        """Gera dados do destinatário"""
        dest = etree.Element("dest")
        
        client = self.invoice.client
        
        # CNPJ ou CPF
        tax_id = re.sub(r'\D', '', client.tax_id or '')
        if len(tax_id) == 14:
            self._add_element(dest, "CNPJ", tax_id)
        else:
            self._add_element(dest, "CPF", tax_id)
        
        # Nome/Razão Social
        self._add_element(dest, "xNome", client.name or "")
        
        # Endereço
        if client.street:
            ender_dest = etree.SubElement(dest, "enderDest")
            self._add_element(ender_dest, "xLgr", client.street or "")
            self._add_element(ender_dest, "nro", client.number or "S/N")
            if client.complement:
                self._add_element(ender_dest, "xCpl", client.complement)
            self._add_element(ender_dest, "xBairro", client.neighborhood or "")
            # Usar código de município do emitente se cliente não tiver
            city_code = getattr(client, 'city_code', None) or self.invoice.issuer_city_code or "4106902"
            self._add_element(ender_dest, "cMun", str(city_code))
            self._add_element(ender_dest, "xMun", client.city or "")
            self._add_element(ender_dest, "UF", client.state or "PR")
            cep = re.sub(r'\D', '', client.zip_code or '')
            self._add_element(ender_dest, "CEP", cep)
            self._add_element(ender_dest, "cPais", "1058")
            self._add_element(ender_dest, "xPais", "Brasil")
            if client.phone:
                phone = re.sub(r'\D', '', client.phone)
                self._add_element(ender_dest, "fone", phone)
        
        # Indicador IE (1=Contribuinte, 2=Isento, 9=Não Contribuinte)
        ind_ie = "9"
        if client.state_registration:
            ind_ie = "1"
            ie = re.sub(r'\D', '', client.state_registration)
            self._add_element(dest, "IE", ie)
        
        self._add_element(dest, "indIEDest", ind_ie)
        
        return dest
    
    def _generate_det(self, item, num_item):
        """Gera item da NF-e"""
        det = etree.Element("det", nItem=str(num_item))
        
        # Produto
        prod = etree.SubElement(det, "prod")
        
        # Código do produto
        self._add_element(prod, "cProd", str(item.code or item.id))
        
        # Código de barras (opcional)
        barcode = getattr(item, 'barcode', None)
        if barcode:
            self._add_element(prod, "cEAN", barcode)
        else:
            self._add_element(prod, "cEAN", "SEM GTIN")
        
        # Descrição
        self._add_element(prod, "xProd", item.description or "")
        
        # NCM
        ncm = re.sub(r'\D', '', item.ncm or '00000000')
        self._add_element(prod, "NCM", ncm)
        
        # CFOP
        self._add_element(prod, "CFOP", str(item.cfop or "5101"))
        
        # Unidade comercial
        self._add_element(prod, "uCom", item.unit or "UN")
        
        # Quantidade comercial
        self._add_element(prod, "qCom", f"{float(item.quantity):.4f}")
        
        # Valor unitário comercial
        self._add_element(prod, "vUnCom", f"{float(item.unit_value):.10f}")
        
        # Valor total bruto
        self._add_element(prod, "vProd", f"{float(item.total_value):.2f}")
        
        # Código de barras tributável
        if barcode:
            self._add_element(prod, "cEANTrib", barcode)
        else:
            self._add_element(prod, "cEANTrib", "SEM GTIN")
        
        # Unidade tributável
        self._add_element(prod, "uTrib", item.unit or "UN")
        
        # Quantidade tributável
        self._add_element(prod, "qTrib", f"{float(item.quantity):.4f}")
        
        # Valor unitário tributável
        self._add_element(prod, "vUnTrib", f"{float(item.unit_value):.10f}")
        
        # Indicador de composição do valor total (0=Entra no total, 1=Não entra)
        self._add_element(prod, "indTot", "1")
        
        # Impostos
        imposto = etree.SubElement(det, "imposto")
        
        # ICMS
        icms = etree.SubElement(imposto, "ICMS")
        
        # Determinar CST/CSOSN baseado no regime
        crt = self.invoice.tax_regime or '3'
        if crt == '1':  # Simples Nacional
            icmssn = etree.SubElement(icms, "ICMSSN102")
            self._add_element(icmssn, "orig", item.icms_origin or "0")
            self._add_element(icmssn, "CSOSN", "102")  # Tributada pelo Simples Nacional sem permissão de crédito
        else:  # Regime Normal
            icms00 = etree.SubElement(icms, "ICMS00")
            self._add_element(icms00, "orig", item.icms_origin or "0")
            self._add_element(icms00, "CST", item.icms_cst or "00")
            self._add_element(icms00, "modBC", "3")  # Valor da operação
            
            # Base de cálculo
            bc_icms = float(item.total_value)
            self._add_element(icms00, "vBC", f"{bc_icms:.2f}")
            
            # Alíquota
            aliq_icms = float(item.icms_rate or 0)
            self._add_element(icms00, "pICMS", f"{aliq_icms:.2f}")
            
            # Valor do ICMS
            v_icms = float(item.icms_value or 0)
            self._add_element(icms00, "vICMS", f"{v_icms:.2f}")
        
        # PIS
        pis = etree.SubElement(imposto, "PIS")
        if float(item.pis_value or 0) > 0:
            pis_aliq = etree.SubElement(pis, "PISAliq")
            self._add_element(pis_aliq, "CST", item.pis_cst or "01")
            self._add_element(pis_aliq, "vBC", f"{float(item.total_value):.2f}")
            self._add_element(pis_aliq, "pPIS", f"{float(item.pis_rate or 0):.2f}")
            self._add_element(pis_aliq, "vPIS", f"{float(item.pis_value):.2f}")
        else:
            pis_nt = etree.SubElement(pis, "PISNT")
            self._add_element(pis_nt, "CST", "07")  # Isenta
        
        # COFINS
        cofins = etree.SubElement(imposto, "COFINS")
        if float(item.cofins_value or 0) > 0:
            cofins_aliq = etree.SubElement(cofins, "COFINSAliq")
            self._add_element(cofins_aliq, "CST", item.cofins_cst or "01")
            self._add_element(cofins_aliq, "vBC", f"{float(item.total_value):.2f}")
            self._add_element(cofins_aliq, "pCOFINS", f"{float(item.cofins_rate or 0):.2f}")
            self._add_element(cofins_aliq, "vCOFINS", f"{float(item.cofins_value):.2f}")
        else:
            cofins_nt = etree.SubElement(cofins, "COFINSNT")
            self._add_element(cofins_nt, "CST", "07")
        
        return det
    
    def _generate_total(self):
        """Gera totalizadores da NF-e"""
        total = etree.Element("total")
        
        # Total de tributos
        icms_tot = etree.SubElement(total, "ICMSTot")
        
        # Base de cálculo do ICMS
        self._add_element(icms_tot, "vBC", f"{float(self.invoice.icms_base or 0):.2f}")
        
        # Valor do ICMS
        self._add_element(icms_tot, "vICMS", f"{float(self.invoice.icms_value or 0):.2f}")
        
        # Valor do ICMS desonerado
        self._add_element(icms_tot, "vICMSDeson", "0.00")
        
        # Base de cálculo ICMS ST
        self._add_element(icms_tot, "vBCST", "0.00")
        
        # Valor ICMS ST
        self._add_element(icms_tot, "vST", "0.00")
        
        # Valor total dos produtos
        self._add_element(icms_tot, "vProd", f"{float(self.invoice.total_products or 0):.2f}")
        
        # Valor do frete
        self._add_element(icms_tot, "vFrete", f"{float(self.invoice.shipping or 0):.2f}")
        
        # Valor do seguro
        self._add_element(icms_tot, "vSeg", f"{float(self.invoice.insurance or 0):.2f}")
        
        # Valor do desconto
        self._add_element(icms_tot, "vDesc", f"{float(self.invoice.discount or 0):.2f}")
        
        # Valor do II
        self._add_element(icms_tot, "vII", "0.00")
        
        # Valor do IPI
        self._add_element(icms_tot, "vIPI", f"{float(self.invoice.ipi_value or 0):.2f}")
        
        # Valor do PIS
        self._add_element(icms_tot, "vPIS", f"{float(self.invoice.pis_value or 0):.2f}")
        
        # Valor do COFINS
        self._add_element(icms_tot, "vCOFINS", f"{float(self.invoice.cofins_value or 0):.2f}")
        
        # Outras despesas
        self._add_element(icms_tot, "vOutro", f"{float(self.invoice.other_expenses or 0):.2f}")
        
        # Valor total da NF-e
        self._add_element(icms_tot, "vNF", f"{float(self.invoice.total_value or 0):.2f}")
        
        return total
    
    def _generate_transp(self):
        """Gera informações de transporte"""
        transp = etree.Element("transp")
        
        # Modalidade do frete (9=Sem frete)
        mod_frete = self.invoice.freight_mode or "9"
        self._add_element(transp, "modFrete", mod_frete)
        
        return transp
    
    def _generate_cobr(self):
        """Gera informações de cobrança"""
        cobr = etree.Element("cobr")
        
        # Fatura
        fat = etree.SubElement(cobr, "fat")
        self._add_element(fat, "nFat", str(self.invoice.number))
        self._add_element(fat, "vOrig", f"{float(self.invoice.total_value or 0):.2f}")
        self._add_element(fat, "vLiq", f"{float(self.invoice.total_value or 0):.2f}")
        
        # Duplicata
        dup = etree.SubElement(cobr, "dup")
        self._add_element(dup, "nDup", str(self.invoice.number).zfill(3))
        if self.invoice.due_date:
            self._add_element(dup, "dVenc", self.invoice.due_date.strftime("%Y-%m-%d"))
        self._add_element(dup, "vDup", f"{float(self.invoice.total_value or 0):.2f}")
        
        return cobr
    
    def _generate_pag(self):
        """Gera forma de pagamento"""
        pag = etree.Element("pag")
        
        det_pag = etree.SubElement(pag, "detPag")
        
        # Tipo de pagamento (01=Dinheiro, 03=Cartão)
        t_pag = "01"
        if self.invoice.payment_method:
            method_map = {
                'dinheiro': '01',
                'cartao': '03',
                'credito': '03',
                'debito': '04',
                'pix': '17',
                'transferencia': '18'
            }
            t_pag = method_map.get(self.invoice.payment_method.lower(), '99')
        
        self._add_element(det_pag, "tPag", t_pag)
        self._add_element(det_pag, "vPag", f"{float(self.invoice.total_value or 0):.2f}")
        
        return pag
    
    def _generate_inf_adic(self):
        """Gera informações adicionais"""
        inf_adic = etree.Element("infAdic")
        
        # Informações adicionais de interesse do Fisco
        if self.invoice.notes:
            self._add_element(inf_adic, "infAdFisco", self.invoice.notes)
        
        # Informações complementares
        if self.invoice.additional_info:
            self._add_element(inf_adic, "infCpl", self.invoice.additional_info)
        
        return inf_adic
    
    def _generate_chave_acesso(self):
        """Gera a chave de acesso de 44 dígitos"""
        # Formato: cUF + AAMM + CNPJ + mod + serie + nNF + tpEmis + cNF + DV
        
        # 1. Código UF (2 dígitos)
        c_uf = str(self._get_uf_code(self.invoice.issuer_state)).zfill(2)
        
        # 2. Ano e mês de emissão (4 dígitos)
        dt_emissao = self.invoice.issue_date or datetime.now()
        aa_mm = dt_emissao.strftime("%y%m")
        
        # 3. CNPJ do emitente (14 dígitos)
        cnpj = re.sub(r'\D', '', self.invoice.issuer_tax_id or '').zfill(14)
        
        # 4. Modelo (2 dígitos) - 55 para NF-e
        mod = "55"
        
        # 5. Série (3 dígitos)
        serie = str(self.invoice.series or 1).zfill(3)
        
        # 6. Número da NF-e (9 dígitos)
        n_nf = str(self.invoice.number).zfill(9)
        
        # 7. Tipo de emissão (1 dígito) - 1 para normal
        tp_emis = "1"
        
        # 8. Código numérico (8 dígitos)
        c_nf = str(self.invoice.id).zfill(8)[-8:]
        
        # Montar chave sem DV
        chave_sem_dv = f"{c_uf}{aa_mm}{cnpj}{mod}{serie}{n_nf}{tp_emis}{c_nf}"
        
        # 9. Calcular DV (1 dígito)
        dv = self._calcular_dv_chave(chave_sem_dv)
        
        return f"{chave_sem_dv}{dv}"
    
    def _calcular_dv_chave(self, chave):
        """Calcula o dígito verificador da chave de acesso usando módulo 11"""
        multiplicador = 2
        soma = 0
        
        for digito in reversed(chave):
            soma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 9:
                multiplicador = 2
        
        resto = soma % 11
        dv = 11 - resto
        
        if dv >= 10:
            dv = 0
        
        return str(dv)
    
    def _get_uf_code(self, uf):
        """Retorna código IBGE da UF"""
        codigos = {
            'AC': 12, 'AL': 27, 'AP': 16, 'AM': 13, 'BA': 29,
            'CE': 23, 'DF': 53, 'ES': 32, 'GO': 52, 'MA': 21,
            'MT': 51, 'MS': 50, 'MG': 31, 'PA': 15, 'PB': 25,
            'PR': 41, 'PE': 26, 'PI': 22, 'RJ': 33, 'RN': 24,
            'RS': 43, 'RO': 11, 'RR': 14, 'SC': 42, 'SP': 35,
            'SE': 28, 'TO': 17
        }
        return codigos.get(uf, 41)
    
    def _add_element(self, parent, tag, text):
        """Adiciona elemento XML com texto"""
        element = etree.SubElement(parent, tag)
        element.text = str(text) if text is not None else ""
        return element
