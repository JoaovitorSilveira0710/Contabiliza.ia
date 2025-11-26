"""
Serviço para emissão de Notas Fiscais Eletrônicas (NFe)
Integração simplificada - Em produção usar biblioteca como python-nfe ou API de gateway
"""

import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class NFeServiceError(Exception):
    """Exceção customizada para erros do serviço de NFe"""
    pass


class NFeService:
    """
    Serviço para emissão e gestão de Notas Fiscais Eletrônicas
    
    NOTA: Esta é uma implementação simplificada para demonstração.
    Em produção, integrar com:
    - API oficial da SEFAZ
    - Gateway de NFe (TecnoSpeed, WebMania, etc)
    - Biblioteca python-nfe
    """
    
    def __init__(self):
        self.ambiente = "homologacao"  # homologacao ou producao
        self.logger = logging.getLogger(__name__)
    
    def gerar_chave_acesso(
        self,
        codigo_uf: str,
        ano_mes: str,
        cnpj: str,
        modelo: str,
        serie: str,
        numero: str,
        forma_emissao: str = "1",
        codigo_numerico: Optional[str] = None
    ) -> str:
        """
        Gera chave de acesso da NFe (44 dígitos)
        
        Formato: UF + AAMM + CNPJ + MOD + SERIE + NNF + TPEMIS + CNF + DV
        
        Args:
            codigo_uf: Código da UF (ex: 35 para SP)
            ano_mes: AAMM (ex: 2411 para nov/2024)
            cnpj: CNPJ do emitente (14 dígitos)
            modelo: Modelo do documento (55=NFe, 65=NFCe)
            serie: Série da nota (3 dígitos)
            numero: Número da nota (9 dígitos)
            forma_emissao: Forma de emissão (1=Normal)
            codigo_numerico: Código numérico aleatório (8 dígitos)
        
        Returns:
            Chave de acesso de 44 dígitos
        """
        try:
            # Limpar CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            
            # Garantir tamanhos corretos
            codigo_uf = str(codigo_uf).zfill(2)
            ano_mes = str(ano_mes).zfill(4)
            cnpj_limpo = cnpj_limpo.zfill(14)
            modelo = str(modelo).zfill(2)
            serie = str(serie).zfill(3)
            numero = str(numero).zfill(9)
            forma_emissao = str(forma_emissao)
            
            # Gerar código numérico aleatório se não fornecido
            if not codigo_numerico:
                codigo_numerico = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            else:
                codigo_numerico = str(codigo_numerico).zfill(8)
            
            # Montar chave sem DV
            chave_sem_dv = (
                codigo_uf +
                ano_mes +
                cnpj_limpo +
                modelo +
                serie +
                numero +
                forma_emissao +
                codigo_numerico
            )
            
            # Calcular dígito verificador (módulo 11)
            dv = self._calcular_dv_modulo11(chave_sem_dv)
            
            # Chave completa
            chave_completa = chave_sem_dv + str(dv)
            
            self.logger.info(f"✅ Chave de acesso gerada: {chave_completa}")
            return chave_completa
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar chave de acesso: {e}")
            raise NFeServiceError(f"Erro ao gerar chave de acesso: {e}")
    
    def _calcular_dv_modulo11(self, chave: str) -> int:
        """
        Calcula dígito verificador usando módulo 11
        """
        multiplicador = 2
        soma = 0
        
        for i in range(len(chave) - 1, -1, -1):
            soma += int(chave[i]) * multiplicador
            multiplicador += 1
            if multiplicador > 9:
                multiplicador = 2
        
        resto = soma % 11
        
        if resto == 0 or resto == 1:
            return 0
        else:
            return 11 - resto
    
    def gerar_protocolo_autorizacao(self) -> str:
        """
        Gera um número de protocolo de autorização simulado
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"{timestamp}{random_digits}"
    
    def validar_dados_emissao(self, dados: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Valida dados obrigatórios para emissão de NFe
        
        Returns:
            (valido, mensagem_erro)
        """
        campos_obrigatorios = [
            'cliente_id',
            'tipo',
            'modelo',
            'serie',
            'numero',
            'data_emissao',
            'cnpj_emitente',
            'nome_emitente',
            'cnpj_destinatario',
            'nome_destinatario',
            'valor_produtos',
            'valor_total'
        ]
        
        # Verificar campos obrigatórios
        for campo in campos_obrigatorios:
            if campo not in dados or dados[campo] is None:
                return False, f"Campo obrigatório ausente: {campo}"
        
        # Validações específicas
        if dados['tipo'] not in ['entrada', 'saida', 'servico']:
            return False, "Tipo inválido (deve ser: entrada, saida ou servico)"
        
        if dados['modelo'] not in ['nfe', 'nfce', 'nfse']:
            return False, "Modelo inválido (deve ser: nfe, nfce ou nfse)"
        
        if dados['valor_total'] <= 0:
            return False, "Valor total deve ser maior que zero"
        
        # Validar CNPJ
        cnpj_emit = ''.join(filter(str.isdigit, dados['cnpj_emitente']))
        cnpj_dest = ''.join(filter(str.isdigit, dados['cnpj_destinatario']))
        
        if len(cnpj_emit) != 14:
            return False, "CNPJ do emitente inválido"
        
        if len(cnpj_dest) not in [11, 14]:  # CPF ou CNPJ
            return False, "CPF/CNPJ do destinatário inválido"
        
        return True, None
    
    async def emitir_nfe(
        self,
        dados_nota: Dict[str, Any],
        itens: list[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Emite uma Nota Fiscal Eletrônica
        
        SIMULAÇÃO - Em produção, fazer integração real com SEFAZ
        
        Args:
            dados_nota: Dados da nota fiscal
            itens: Lista de itens da nota (opcional)
        
        Returns:
            Dicionário com resultado da emissão
        """
        try:
            self.logger.info(f"📤 Iniciando emissão de NFe - Número: {dados_nota.get('numero')}")
            
            # 1. Validar dados
            valido, erro = self.validar_dados_emissao(dados_nota)
            if not valido:
                raise NFeServiceError(f"Validação falhou: {erro}")
            
            # 2. Gerar chave de acesso
            hoje = datetime.now()
            codigo_uf = "35"  # SP - em produção pegar do cadastro
            ano_mes = hoje.strftime("%y%m")
            
            chave_acesso = self.gerar_chave_acesso(
                codigo_uf=codigo_uf,
                ano_mes=ano_mes,
                cnpj=dados_nota['cnpj_emitente'],
                modelo="55" if dados_nota['modelo'] == 'nfe' else "65",
                serie=str(dados_nota['serie']),
                numero=str(dados_nota['numero'])
            )
            
            # 3. Montar XML da NFe (simulação)
            xml_nfe = self._montar_xml_nfe(dados_nota, chave_acesso, itens)
            
            # 4. Assinar XML (simulação)
            self.logger.info("🔐 Assinando XML da NFe...")
            xml_assinado = xml_nfe  # Em produção, assinar com certificado digital
            
            # 5. Transmitir para SEFAZ (simulação)
            self.logger.info("📡 Transmitindo NFe para SEFAZ...")
            resultado_transmissao = await self._transmitir_sefaz(xml_assinado, chave_acesso)
            
            # 6. Processar retorno
            if resultado_transmissao['status'] == 'autorizada':
                self.logger.info(f"✅ NFe autorizada - Protocolo: {resultado_transmissao['protocolo']}")
                
                return {
                    "sucesso": True,
                    "status": "autorizada",
                    "chave_acesso": chave_acesso,
                    "protocolo": resultado_transmissao['protocolo'],
                    "data_autorizacao": resultado_transmissao['data_hora'],
                    "mensagem": "Nota fiscal autorizada com sucesso",
                    "xml": xml_assinado
                }
            else:
                raise NFeServiceError(f"Erro na autorização: {resultado_transmissao.get('motivo')}")
                
        except NFeServiceError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro ao emitir NFe: {e}")
            raise NFeServiceError(f"Erro inesperado na emissão: {e}")
    
    def _montar_xml_nfe(
        self,
        dados: Dict[str, Any],
        chave_acesso: str,
        itens: list[Dict[str, Any]] = None
    ) -> str:
        """
        Monta XML da NFe (versão simplificada)
        Em produção, usar biblioteca especializada
        """
        # Versão simplificada do XML para demonstração
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <NFe>
        <infNFe Id="NFe{chave_acesso}" versao="4.00">
            <ide>
                <cUF>35</cUF>
                <cNF>{chave_acesso[35:43]}</cNF>
                <natOp>Venda de mercadoria</natOp>
                <mod>55</mod>
                <serie>{dados['serie']}</serie>
                <nNF>{dados['numero']}</nNF>
                <dhEmi>{dados['data_emissao'].isoformat()}</dhEmi>
                <tpNF>{1 if dados['tipo'] == 'saida' else 0}</tpNF>
                <tpAmb>2</tpAmb>
                <finNFe>1</finNFe>
            </ide>
            <emit>
                <CNPJ>{dados['cnpj_emitente']}</CNPJ>
                <xNome>{dados['nome_emitente']}</xNome>
            </emit>
            <dest>
                <{'CNPJ' if len(''.join(filter(str.isdigit, dados['cnpj_destinatario']))) == 14 else 'CPF'}>{dados['cnpj_destinatario']}</{'CNPJ' if len(''.join(filter(str.isdigit, dados['cnpj_destinatario']))) == 14 else 'CPF'}>
                <xNome>{dados['nome_destinatario']}</xNome>
            </dest>
            <total>
                <ICMSTot>
                    <vProd>{dados['valor_produtos']:.2f}</vProd>
                    <vNF>{dados['valor_total']:.2f}</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
</nfeProc>"""
        
        return xml
    
    async def _transmitir_sefaz(self, xml: str, chave_acesso: str) -> Dict[str, Any]:
        """
        Simula transmissão para SEFAZ
        Em produção, fazer requisição SOAP para webservice da SEFAZ
        """
        import asyncio
        
        # Simular delay de processamento
        await asyncio.sleep(2)
        
        # Simular resposta da SEFAZ (95% de sucesso)
        if random.random() < 0.95:
            return {
                "status": "autorizada",
                "protocolo": self.gerar_protocolo_autorizacao(),
                "data_hora": datetime.now(),
                "codigo": "100",
                "motivo": "Autorizado o uso da NF-e"
            }
        else:
            return {
                "status": "rejeitada",
                "protocolo": None,
                "data_hora": datetime.now(),
                "codigo": "539",
                "motivo": "CNPJ do emitente não cadastrado"
            }
    
    async def consultar_status_nfe(self, chave_acesso: str) -> Dict[str, Any]:
        """
        Consulta status de uma NFe na SEFAZ
        """
        try:
            self.logger.info(f"🔍 Consultando status da NFe: {chave_acesso}")
            
            # Simular consulta
            import asyncio
            await asyncio.sleep(1)
            
            return {
                "chave_acesso": chave_acesso,
                "status": "autorizada",
                "protocolo": self.gerar_protocolo_autorizacao(),
                "data_autorizacao": datetime.now() - timedelta(days=random.randint(1, 30)),
                "situacao": "Normal"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao consultar status: {e}")
            raise NFeServiceError(f"Erro na consulta: {e}")
    
    async def cancelar_nfe(
        self,
        chave_acesso: str,
        protocolo: str,
        justificativa: str
    ) -> Dict[str, Any]:
        """
        Cancela uma NFe autorizada
        Justificativa deve ter no mínimo 15 caracteres
        """
        try:
            self.logger.info(f"🚫 Cancelando NFe: {chave_acesso}")
            
            # Validar justificativa
            if len(justificativa) < 15:
                raise NFeServiceError("Justificativa deve ter no mínimo 15 caracteres")
            
            # Simular cancelamento
            import asyncio
            await asyncio.sleep(1.5)
            
            protocolo_cancelamento = self.gerar_protocolo_autorizacao()
            
            return {
                "sucesso": True,
                "chave_acesso": chave_acesso,
                "protocolo_cancelamento": protocolo_cancelamento,
                "data_cancelamento": datetime.now(),
                "mensagem": "NFe cancelada com sucesso"
            }
            
        except NFeServiceError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro ao cancelar NFe: {e}")
            raise NFeServiceError(f"Erro no cancelamento: {e}")
    
    async def inutilizar_numeracao(
        self,
        cnpj: str,
        serie: str,
        numero_inicial: int,
        numero_final: int,
        justificativa: str
    ) -> Dict[str, Any]:
        """
        Inutiliza numeração de NFe
        """
        try:
            self.logger.info(f"⛔ Inutilizando numeração {numero_inicial} a {numero_final}")
            
            if len(justificativa) < 15:
                raise NFeServiceError("Justificativa deve ter no mínimo 15 caracteres")
            
            # Simular inutilização
            import asyncio
            await asyncio.sleep(1)
            
            return {
                "sucesso": True,
                "protocolo": self.gerar_protocolo_autorizacao(),
                "data": datetime.now(),
                "mensagem": f"Numeração {numero_inicial} a {numero_final} inutilizada"
            }
            
        except NFeServiceError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro ao inutilizar numeração: {e}")
            raise NFeServiceError(f"Erro na inutilização: {e}")
    
    def validar_certificado_digital(self, certificado_path: str, senha: str) -> bool:
        """
        Valida certificado digital A1
        Em produção, validar arquivo .pfx e senha
        """
        try:
            # Simulação
            self.logger.info("🔐 Validando certificado digital...")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao validar certificado: {e}")
            return False
    
    def gerar_danfe_pdf(self, xml_nfe: str) -> bytes:
        """
        Gera DANFE (Documento Auxiliar da NFe) em PDF
        Em produção, usar biblioteca como BrasilAPI-DANFE ou similar
        """
        try:
            self.logger.info("📄 Gerando DANFE em PDF...")
            
            # Simulação - retorna bytes vazios
            # Em produção, gerar PDF real do DANFE
            return b"PDF_CONTENT_HERE"
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar DANFE: {e}")
            raise NFeServiceError(f"Erro ao gerar DANFE: {e}")


# Instância global do serviço
nfe_service = NFeService()
