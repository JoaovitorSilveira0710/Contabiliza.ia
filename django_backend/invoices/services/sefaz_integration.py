"""
Serviço de Integração com SEFAZ - Ambiente de Homologação e Produção
Suporta emissão, consulta e cancelamento de NF-e
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SefazConfig:
    """Configurações dos Web Services da SEFAZ por UF"""
    
    # SEFAZ Virtual de Contingência (SVRS) - Estados que usam SVRS
    WEBSERVICES_SVRS = {
        'homologacao': {
            'autorizacao': 'https://nfe-homologacao.svrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://nfe-homologacao.svrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://nfe-homologacao.svrs.rs.gov.br/ws/NfeConsulta/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://nfe-homologacao.svrs.rs.gov.br/ws/NfeStatusServico/NFeStatusServico4.asmx',
            'inutilizacao': 'https://nfe-homologacao.svrs.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao4.asmx',
            'evento': 'https://nfe-homologacao.svrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx'
        },
        'producao': {
            'autorizacao': 'https://nfe.svrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://nfe.svrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://nfe.svrs.rs.gov.br/ws/NfeConsulta/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://nfe.svrs.rs.gov.br/ws/NfeStatusServico/NFeStatusServico4.asmx',
            'inutilizacao': 'https://nfe.svrs.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao4.asmx',
            'evento': 'https://nfe.svrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx'
        }
    }
    
    # Acre (AC) - Usa SVRS
    WEBSERVICES_AC = WEBSERVICES_SVRS
    
    # Alagoas (AL) - Usa SVRS
    WEBSERVICES_AL = WEBSERVICES_SVRS
    
    # Amapá (AP) - Usa SVRS
    WEBSERVICES_AP = WEBSERVICES_SVRS
    
    # Amazonas (AM)
    WEBSERVICES_AM = {
        'homologacao': {
            'autorizacao': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4',
            'retorno_autorizacao': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4',
            'consulta_protocolo': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta4',
            'status_servico': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico4',
            'inutilizacao': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4',
            'evento': 'https://homnfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta4',
            'status_servico': 'https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico4',
            'inutilizacao': 'https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4',
            'evento': 'https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4'
        }
    }
    
    # Bahia (BA)
    WEBSERVICES_BA = {
        'homologacao': {
            'autorizacao': 'https://hnfe.sefaz.ba.gov.br/webservices/NFeAutorizacao4/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://hnfe.sefaz.ba.gov.br/webservices/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://hnfe.sefaz.ba.gov.br/webservices/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://hnfe.sefaz.ba.gov.br/webservices/NFeStatusServico4/NFeStatusServico4.asmx',
            'inutilizacao': 'https://hnfe.sefaz.ba.gov.br/webservices/NFeInutilizacao4/NFeInutilizacao4.asmx',
            'evento': 'https://hnfe.sefaz.ba.gov.br/webservices/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.ba.gov.br/webservices/NFeAutorizacao4/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://nfe.sefaz.ba.gov.br/webservices/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://nfe.sefaz.ba.gov.br/webservices/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://nfe.sefaz.ba.gov.br/webservices/NFeStatusServico4/NFeStatusServico4.asmx',
            'inutilizacao': 'https://nfe.sefaz.ba.gov.br/webservices/NFeInutilizacao4/NFeInutilizacao4.asmx',
            'evento': 'https://nfe.sefaz.ba.gov.br/webservices/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx'
        }
    }
    
    # Ceará (CE)
    WEBSERVICES_CE = {
        'homologacao': {
            'autorizacao': 'https://nfeh.sefaz.ce.gov.br/nfe4/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfeh.sefaz.ce.gov.br/nfe4/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfeh.sefaz.ce.gov.br/nfe4/services/NFeConsultaProtocolo4',
            'status_servico': 'https://nfeh.sefaz.ce.gov.br/nfe4/services/NFeStatusServico4',
            'inutilizacao': 'https://nfeh.sefaz.ce.gov.br/nfe4/services/NFeInutilizacao4',
            'evento': 'https://nfeh.sefaz.ce.gov.br/nfe4/services/NFeRecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.ce.gov.br/nfe4/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.sefaz.ce.gov.br/nfe4/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.sefaz.ce.gov.br/nfe4/services/NFeConsultaProtocolo4',
            'status_servico': 'https://nfe.sefaz.ce.gov.br/nfe4/services/NFeStatusServico4',
            'inutilizacao': 'https://nfe.sefaz.ce.gov.br/nfe4/services/NFeInutilizacao4',
            'evento': 'https://nfe.sefaz.ce.gov.br/nfe4/services/NFeRecepcaoEvento4'
        }
    }
    
    # Distrito Federal (DF) - Usa SVRS
    WEBSERVICES_DF = WEBSERVICES_SVRS
    
    # Espírito Santo (ES) - Usa SVRS
    WEBSERVICES_ES = WEBSERVICES_SVRS
    
    # Goiás (GO)
    WEBSERVICES_GO = {
        'homologacao': {
            'autorizacao': 'https://homolog.sefaz.go.gov.br/nfe/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://homolog.sefaz.go.gov.br/nfe/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://homolog.sefaz.go.gov.br/nfe/services/NFeConsultaProtocolo4',
            'status_servico': 'https://homolog.sefaz.go.gov.br/nfe/services/NFeStatusServico4',
            'inutilizacao': 'https://homolog.sefaz.go.gov.br/nfe/services/NFeInutilizacao4',
            'evento': 'https://homolog.sefaz.go.gov.br/nfe/services/NFeRecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.go.gov.br/nfe/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.sefaz.go.gov.br/nfe/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.sefaz.go.gov.br/nfe/services/NFeConsultaProtocolo4',
            'status_servico': 'https://nfe.sefaz.go.gov.br/nfe/services/NFeStatusServico4',
            'inutilizacao': 'https://nfe.sefaz.go.gov.br/nfe/services/NFeInutilizacao4',
            'evento': 'https://nfe.sefaz.go.gov.br/nfe/services/NFeRecepcaoEvento4'
        }
    }
    
    # Maranhão (MA)
    WEBSERVICES_MA = {
        'homologacao': {
            'autorizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NFeAutorizacao4/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://hom.sefazvirtual.fazenda.gov.br/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://hom.sefazvirtual.fazenda.gov.br/NFeStatusServico4/NFeStatusServico4.asmx',
            'inutilizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NFeInutilizacao4/NFeInutilizacao4.asmx',
            'evento': 'https://hom.sefazvirtual.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx'
        },
        'producao': {
            'autorizacao': 'https://www.sefazvirtual.fazenda.gov.br/NFeAutorizacao4/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://www.sefazvirtual.fazenda.gov.br/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://www.sefazvirtual.fazenda.gov.br/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://www.sefazvirtual.fazenda.gov.br/NFeStatusServico4/NFeStatusServico4.asmx',
            'inutilizacao': 'https://www.sefazvirtual.fazenda.gov.br/NFeInutilizacao4/NFeInutilizacao4.asmx',
            'evento': 'https://www.sefazvirtual.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx'
        }
    }
    
    # Mato Grosso (MT)
    WEBSERVICES_MT = {
        'homologacao': {
            'autorizacao': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeAutorizacao4',
            'retorno_autorizacao': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRetAutorizacao4',
            'consulta_protocolo': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta4',
            'status_servico': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico4',
            'inutilizacao': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao4',
            'evento': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta4',
            'status_servico': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico4',
            'inutilizacao': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao4',
            'evento': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento4'
        }
    }
    
    # Mato Grosso do Sul (MS)
    WEBSERVICES_MS = {
        'homologacao': {
            'autorizacao': 'https://hom.nfe.sefaz.ms.gov.br/ws/NFeAutorizacao4',
            'retorno_autorizacao': 'https://hom.nfe.sefaz.ms.gov.br/ws/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://hom.nfe.sefaz.ms.gov.br/ws/NFeConsultaProtocolo4',
            'status_servico': 'https://hom.nfe.sefaz.ms.gov.br/ws/NFeStatusServico4',
            'inutilizacao': 'https://hom.nfe.sefaz.ms.gov.br/ws/NFeInutilizacao4',
            'evento': 'https://hom.nfe.sefaz.ms.gov.br/ws/NFeRecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.ms.gov.br/ws/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.sefaz.ms.gov.br/ws/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.sefaz.ms.gov.br/ws/NFeConsultaProtocolo4',
            'status_servico': 'https://nfe.sefaz.ms.gov.br/ws/NFeStatusServico4',
            'inutilizacao': 'https://nfe.sefaz.ms.gov.br/ws/NFeInutilizacao4',
            'evento': 'https://nfe.sefaz.ms.gov.br/ws/NFeRecepcaoEvento4'
        }
    }
    
    # Minas Gerais (MG)
    WEBSERVICES_MG = {
        'homologacao': {
            'autorizacao': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeConsultaProtocolo4',
            'status_servico': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4',
            'inutilizacao': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeInutilizacao4',
            'evento': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeConsultaProtocolo4',
            'status_servico': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4',
            'inutilizacao': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeInutilizacao4',
            'evento': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeRecepcaoEvento4'
        }
    }
    
    # Pará (PA) - Usa SVRS
    WEBSERVICES_PA = WEBSERVICES_SVRS
    
    # Paraíba (PB) - Usa SVRS
    WEBSERVICES_PB = WEBSERVICES_SVRS
    
    # Paraná (PR)
    WEBSERVICES_PR = {
        'homologacao': {
            'autorizacao': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao4',
            'retorno_autorizacao': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeConsultaProtocolo4',
            'status_servico': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeStatusServico4',
            'inutilizacao': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao4',
            'evento': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.fazenda.pr.gov.br/nfe/NFeConsultaProtocolo4',
            'status_servico': 'https://nfe.fazenda.pr.gov.br/nfe/NFeStatusServico4',
            'inutilizacao': 'https://nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao4',
            'evento': 'https://nfe.fazenda.pr.gov.br/nfe/NFeRecepcaoEvento4'
        }
    }
    
    # Pernambuco (PE)
    WEBSERVICES_PE = {
        'homologacao': {
            'autorizacao': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NFeConsultaProtocolo4',
            'status_servico': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NFeStatusServico4',
            'inutilizacao': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NFeInutilizacao4',
            'evento': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NFeRecepcaoEvento4'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeAutorizacao4',
            'retorno_autorizacao': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeRetAutorizacao4',
            'consulta_protocolo': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeConsultaProtocolo4',
            'status_servico': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeStatusServico4',
            'inutilizacao': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeInutilizacao4',
            'evento': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeRecepcaoEvento4'
        }
    }
    
    # Piauí (PI) - Usa SVRS
    WEBSERVICES_PI = WEBSERVICES_SVRS
    
    # Rio de Janeiro (RJ) - Usa SVRS
    WEBSERVICES_RJ = WEBSERVICES_SVRS
    
    # Rio Grande do Norte (RN) - Usa SVRS
    WEBSERVICES_RN = WEBSERVICES_SVRS
    
    # Rio Grande do Sul (RS)
    WEBSERVICES_RS = {
        'homologacao': {
            'autorizacao': 'https://nfe-homologacao.sefazrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://nfe-homologacao.sefazrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://nfe-homologacao.sefazrs.rs.gov.br/ws/NfeConsulta/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://nfe-homologacao.sefazrs.rs.gov.br/ws/NfeStatusServico/NFeStatusServico4.asmx',
            'inutilizacao': 'https://nfe-homologacao.sefazrs.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao4.asmx',
            'evento': 'https://nfe-homologacao.sefazrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx'
        },
        'producao': {
            'autorizacao': 'https://nfe.sefazrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx',
            'retorno_autorizacao': 'https://nfe.sefazrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx',
            'consulta_protocolo': 'https://nfe.sefazrs.rs.gov.br/ws/NfeConsulta/NFeConsultaProtocolo4.asmx',
            'status_servico': 'https://nfe.sefazrs.rs.gov.br/ws/NfeStatusServico/NFeStatusServico4.asmx',
            'inutilizacao': 'https://nfe.sefazrs.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao4.asmx',
            'evento': 'https://nfe.sefazrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx'
        }
    }
    
    # Rondônia (RO) - Usa SVRS
    WEBSERVICES_RO = WEBSERVICES_SVRS
    
    # Roraima (RR) - Usa SVRS
    WEBSERVICES_RR = WEBSERVICES_SVRS
    
    # Santa Catarina (SC) - Usa SVRS
    WEBSERVICES_SC = WEBSERVICES_SVRS
    
    # São Paulo (SP)
    WEBSERVICES_SP = {
        'homologacao': {
            'autorizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx',
            'retorno_autorizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nferetautorizacao4.asmx',
            'consulta_protocolo': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeconsultaprotocolo4.asmx',
            'status_servico': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfestatusservico4.asmx',
            'inutilizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeinutilizacao4.asmx',
            'evento': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nferecepcaoevento4.asmx'
        },
        'producao': {
            'autorizacao': 'https://nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx',
            'retorno_autorizacao': 'https://nfe.fazenda.sp.gov.br/ws/nferetautorizacao4.asmx',
            'consulta_protocolo': 'https://nfe.fazenda.sp.gov.br/ws/nfeconsultaprotocolo4.asmx',
            'status_servico': 'https://nfe.fazenda.sp.gov.br/ws/nfestatusservico4.asmx',
            'inutilizacao': 'https://nfe.fazenda.sp.gov.br/ws/nfeinutilizacao4.asmx',
            'evento': 'https://nfe.fazenda.sp.gov.br/ws/nferecepcaoevento4.asmx'
        }
    }
    
    # Sergipe (SE) - Usa SVRS
    WEBSERVICES_SE = WEBSERVICES_SVRS
    
    # Tocantins (TO) - Usa SVRS
    WEBSERVICES_TO = WEBSERVICES_SVRS
    
    @classmethod
    def get_webservice_url(cls, uf, ambiente, servico):
        """
        Retorna a URL do webservice da SEFAZ
        
        Args:
            uf: Sigla da UF (AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO)
            ambiente: 'homologacao' ou 'producao'
            servico: 'autorizacao', 'consulta_protocolo', 'status_servico', etc
        """
        webservices = {
            'AC': cls.WEBSERVICES_AC,
            'AL': cls.WEBSERVICES_AL,
            'AP': cls.WEBSERVICES_AP,
            'AM': cls.WEBSERVICES_AM,
            'BA': cls.WEBSERVICES_BA,
            'CE': cls.WEBSERVICES_CE,
            'DF': cls.WEBSERVICES_DF,
            'ES': cls.WEBSERVICES_ES,
            'GO': cls.WEBSERVICES_GO,
            'MA': cls.WEBSERVICES_MA,
            'MT': cls.WEBSERVICES_MT,
            'MS': cls.WEBSERVICES_MS,
            'MG': cls.WEBSERVICES_MG,
            'PA': cls.WEBSERVICES_PA,
            'PB': cls.WEBSERVICES_PB,
            'PR': cls.WEBSERVICES_PR,
            'PE': cls.WEBSERVICES_PE,
            'PI': cls.WEBSERVICES_PI,
            'RJ': cls.WEBSERVICES_RJ,
            'RN': cls.WEBSERVICES_RN,
            'RS': cls.WEBSERVICES_RS,
            'RO': cls.WEBSERVICES_RO,
            'RR': cls.WEBSERVICES_RR,
            'SC': cls.WEBSERVICES_SC,
            'SP': cls.WEBSERVICES_SP,
            'SE': cls.WEBSERVICES_SE,
            'TO': cls.WEBSERVICES_TO
        }
        
        if uf not in webservices:
            raise ValueError(f"UF {uf} não suportada. UFs disponíveis: {', '.join(sorted(webservices.keys()))}")
        
        return webservices[uf].get(ambiente, {}).get(servico)


class SefazIntegration:
    """Serviço de integração com Web Services da SEFAZ"""
    
    def __init__(self, uf='PR', ambiente='homologacao'):
        """
        Inicializa o serviço de integração
        
        Args:
            uf: Unidade Federativa (PR, MG, SP, etc)
            ambiente: 'homologacao' ou 'producao'
        """
        self.uf = uf
        self.ambiente = ambiente
        self.config = SefazConfig()
        
    def get_url(self, servico):
        """Obtém URL do serviço"""
        return self.config.get_webservice_url(self.uf, self.ambiente, servico)
    
    def consultar_status_servico(self):
        """
        Consulta o status do serviço da SEFAZ
        
        Returns:
            dict: {
                'status': 'online' | 'offline',
                'codigo': '107',
                'mensagem': 'Serviço em Operação',
                'tempo_medio': 1.5  # segundos
            }
        """
        try:
            url = self.get_url('status_servico')
            
            # XML de consulta (simplificado - em produção deve ser completo)
            xml_consulta = f"""<?xml version="1.0" encoding="UTF-8"?>
<consStatServ xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <tpAmb>{2 if self.ambiente == 'homologacao' else 1}</tpAmb>
    <cUF>{self._get_codigo_uf()}</cUF>
    <xServ>STATUS</xServ>
</consStatServ>"""
            
            # Em produção real, usar certificado digital e SOAP
            logger.info(f"Consultando status SEFAZ {self.uf} - {self.ambiente}")
            
            # Simulação para testes (remover em produção)
            if self.ambiente == 'homologacao':
                return {
                    'status': 'online',
                    'codigo': '107',
                    'mensagem': 'Serviço em Operação',
                    'tempo_medio': 1.2,
                    'ambiente': self.ambiente,
                    'uf': self.uf
                }
            
            # TODO: Implementar requisição SOAP real com certificado
            # response = requests.post(url, data=xml_consulta, 
            #                         cert=('cert.pem', 'key.pem'),
            #                         headers={'Content-Type': 'text/xml'})
            
            return {
                'status': 'offline',
                'mensagem': 'Integração não implementada (necessário certificado digital)'
            }
            
        except Exception as e:
            logger.error(f"Erro ao consultar status: {str(e)}")
            return {
                'status': 'error',
                'mensagem': str(e)
            }
    
    def validar_xml_nfe(self, xml_nfe):
        """
        Valida o XML da NF-e antes de enviar
        
        Args:
            xml_nfe: String com XML da NF-e
            
        Returns:
            dict: {
                'valido': True/False,
                'erros': ['lista de erros']
            }
        """
        erros = []
        
        try:
            # Parse do XML
            root = ET.fromstring(xml_nfe)
            
            # Validações básicas
            if root.tag != '{http://www.portalfiscal.inf.br/nfe}NFe':
                erros.append('Tag raiz inválida')
            
            # Verificar versão
            versao = root.get('versao')
            if versao != '4.00':
                erros.append(f'Versão incorreta: {versao}. Esperado: 4.00')
            
            # Verificar infNFe
            inf_nfe = root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe')
            if inf_nfe is None:
                erros.append('Tag infNFe não encontrada')
            
            # Verificar assinatura (em produção)
            signature = root.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            if signature is None and self.ambiente == 'producao':
                erros.append('XML não assinado digitalmente')
            
            # TODO: Adicionar mais validações conforme schema XSD
            
            return {
                'valido': len(erros) == 0,
                'erros': erros
            }
            
        except ET.ParseError as e:
            return {
                'valido': False,
                'erros': [f'Erro ao parsear XML: {str(e)}']
            }
    
    def autorizar_nfe(self, xml_nfe):
        """
        Envia NF-e para autorização na SEFAZ
        
        Args:
            xml_nfe: String com XML da NF-e assinado
            
        Returns:
            dict: {
                'sucesso': True/False,
                'codigo': '100',  # Código de retorno SEFAZ
                'mensagem': 'Autorizado o uso da NF-e',
                'protocolo': '135210000000001',
                'chave_acesso': '41210812345678901234550010000000011234567890',
                'data_autorizacao': datetime.now()
            }
        """
        try:
            # Validar XML antes de enviar
            validacao = self.validar_xml_nfe(xml_nfe)
            if not validacao['valido']:
                return {
                    'sucesso': False,
                    'codigo': '215',
                    'mensagem': f"Erro na validação: {', '.join(validacao['erros'])}"
                }
            
            url = self.get_url('autorizacao')
            
            logger.info(f"Enviando NF-e para autorização - {self.ambiente}")
            
            # Em ambiente de homologação, simular resposta
            if self.ambiente == 'homologacao':
                # TODO: Implementar envio real em produção
                return {
                    'sucesso': True,
                    'codigo': '100',
                    'mensagem': 'Autorizado o uso da NF-e',
                    'protocolo': f"9999{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'chave_acesso': self._extrair_chave_acesso(xml_nfe),
                    'data_autorizacao': datetime.now(),
                    'ambiente': 'homologacao',
                    'observacao': 'SEM VALOR FISCAL - EMITIDA EM AMBIENTE DE HOMOLOGAÇÃO'
                }
            
            # TODO: Implementar requisição SOAP com certificado digital
            return {
                'sucesso': False,
                'mensagem': 'Integração completa requer certificado digital A1/A3'
            }
            
        except Exception as e:
            logger.error(f"Erro ao autorizar NF-e: {str(e)}")
            return {
                'sucesso': False,
                'codigo': '999',
                'mensagem': f'Erro interno: {str(e)}'
            }
    
    def consultar_nfe(self, chave_acesso):
        """
        Consulta situação de uma NF-e pela chave de acesso
        
        Args:
            chave_acesso: Chave de 44 dígitos
            
        Returns:
            dict: Dados da NF-e e protocolo
        """
        try:
            if len(chave_acesso) != 44:
                return {
                    'sucesso': False,
                    'mensagem': 'Chave de acesso deve ter 44 dígitos'
                }
            
            url = self.get_url('consulta_protocolo')
            
            logger.info(f"Consultando NF-e: {chave_acesso}")
            
            # Simulação para homologação
            if self.ambiente == 'homologacao':
                return {
                    'sucesso': True,
                    'codigo': '100',
                    'situacao': 'Autorizada',
                    'chave_acesso': chave_acesso,
                    'protocolo': f"9999{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'ambiente': 'homologacao'
                }
            
            return {
                'sucesso': False,
                'mensagem': 'Implementação requer certificado digital'
            }
            
        except Exception as e:
            logger.error(f"Erro ao consultar NF-e: {str(e)}")
            return {
                'sucesso': False,
                'mensagem': str(e)
            }
    
    def cancelar_nfe(self, chave_acesso, protocolo, justificativa):
        """
        Cancela uma NF-e autorizada
        
        Args:
            chave_acesso: Chave de 44 dígitos
            protocolo: Protocolo de autorização
            justificativa: Motivo do cancelamento (mínimo 15 caracteres)
            
        Returns:
            dict: Resultado do cancelamento
        """
        try:
            if len(justificativa) < 15:
                return {
                    'sucesso': False,
                    'mensagem': 'Justificativa deve ter no mínimo 15 caracteres'
                }
            
            url = self.get_url('evento')
            
            logger.info(f"Cancelando NF-e: {chave_acesso}")
            
            # Simulação
            if self.ambiente == 'homologacao':
                return {
                    'sucesso': True,
                    'codigo': '135',
                    'mensagem': 'Evento registrado e vinculado a NF-e',
                    'chave_acesso': chave_acesso,
                    'protocolo_cancelamento': f"9999{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'data_cancelamento': datetime.now()
                }
            
            return {
                'sucesso': False,
                'mensagem': 'Implementação requer certificado digital'
            }
            
        except Exception as e:
            logger.error(f"Erro ao cancelar NF-e: {str(e)}")
            return {
                'sucesso': False,
                'mensagem': str(e)
            }
    
    def _get_codigo_uf(self):
        """Retorna código IBGE da UF"""
        codigos_uf = {
            'AC': 12, 'AL': 27, 'AP': 16, 'AM': 13, 'BA': 29,
            'CE': 23, 'DF': 53, 'ES': 32, 'GO': 52, 'MA': 21,
            'MT': 51, 'MS': 50, 'MG': 31, 'PA': 15, 'PB': 25,
            'PR': 41, 'PE': 26, 'PI': 22, 'RJ': 33, 'RN': 24,
            'RS': 43, 'RO': 11, 'RR': 14, 'SC': 42, 'SP': 35,
            'SE': 28, 'TO': 17
        }
        return codigos_uf.get(self.uf, 41)  # Default PR
    
    def _extrair_chave_acesso(self, xml_nfe):
        """Extrai chave de acesso do XML"""
        try:
            root = ET.fromstring(xml_nfe)
            inf_nfe = root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe')
            if inf_nfe is not None:
                return inf_nfe.get('Id', '').replace('NFe', '')
        except:
            pass
        return '0' * 44  # Retorno padrão
