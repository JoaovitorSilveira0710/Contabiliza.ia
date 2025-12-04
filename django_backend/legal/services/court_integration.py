"""
Court Integration Service for Brazilian Courts
Fetches process information through public APIs and web scraping
"""
import re
import requests
from datetime import datetime
from typing import Dict, Optional, List


class CourtIntegrationService:
    """
    Service for querying legal processes in Brazilian courts
    """
    
    # Supported courts
    SUPPORTED_COURTS = {
        'TJPR': 'Tribunal de Justiça do Paraná',
        'TJSP': 'Tribunal de Justiça de São Paulo',
        'TJRJ': 'Tribunal de Justiça do Rio de Janeiro',
        'TJRS': 'Tribunal de Justiça do Rio Grande do Sul',
        'TJMG': 'Tribunal de Justiça de Minas Gerais',
        'TJSC': 'Tribunal de Justiça de Santa Catarina',
        'TST': 'Tribunal Superior do Trabalho',
        'TRT9': 'Tribunal Regional do Trabalho 9ª Região (PR)',
    }
    
    @staticmethod
    def normalize_process_number(process_number: str) -> str:
        """
        Normalizes process number by removing formatting
        CNJ Format: NNNNNNN-DD.AAAA.J.TR.OOOO
        """
        clean_number = re.sub(r'\D', '', process_number)
        
        if len(clean_number) != 20:
            raise ValueError(f"Invalid process number. Expected 20 digits, received {len(clean_number)}")
        
        return clean_number
    
    @staticmethod
    def format_process_number(process_number: str) -> str:
        """
        Formats process number in CNJ standard
        NNNNNNN-DD.AAAA.J.TR.OOOO
        """
        clean = CourtIntegrationService.normalize_process_number(process_number)
        
        return f"{clean[0:7]}-{clean[7:9]}.{clean[9:13]}.{clean[13]}.{clean[14:16]}.{clean[16:20]}"
    
    @staticmethod
    def identify_court(process_number: str) -> Optional[str]:
        """
        Identifies court based on CNJ process number
        Position 14-15: Court code
        """
        try:
            clean = CourtIntegrationService.normalize_process_number(process_number)
            court_code = clean[14:16]
            
            court_mapping = {
                '16': 'TJPR',
                '26': 'TJSP',
                '19': 'TJRJ',
                '21': 'TJRS',
                '13': 'TJMG',
                '24': 'TJSC',
                '09': 'TRT9',
            }
            
            return court_mapping.get(court_code)
        except:
            return None
    
    @classmethod
    def search_process(cls, process_number: str) -> Dict:
        """
        Searches for process information in court systems
        """
        try:
            formatted_number = cls.format_process_number(process_number)
            court = cls.identify_court(process_number)
            
            if not court:
                return {
                    'success': False,
                    'error': 'Court not identified or not supported',
                    'process_number': formatted_number
                }
            
            # Try to search in specific court
            if court == 'TJPR':
                return cls._search_tjpr(formatted_number)
            elif court == 'TJSP':
                return cls._search_tjsp(formatted_number)
            elif court == 'TRT9':
                return cls._search_trt9(formatted_number)
            else:
                return {
                    'success': False,
                    'error': f'Integration with {court} not yet implemented',
                    'process_number': formatted_number,
                    'court': court
                }
                
        except ValueError as e:
            return {
                'success': False,
                'error': str(e),
                'process_number': process_number
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error searching for process: {str(e)}',
                'process_number': process_number
            }
    
    @staticmethod
    def _search_tjpr(process_number: str) -> Dict:
        """
        Search process in TJPR (Paraná Court of Justice)
        API: https://portal.tjpr.jus.br/consulta-processual
        """
        try:
            url = f"https://portal.tjpr.jus.br/consultaprocessual/api/processos/{process_number}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'process_number': process_number,
                    'court': 'TJPR',
                    'data': {
                        'numero_processo': process_number,
                        'vara': data.get('orgao', 'Not informed'),
                        'assunto': data.get('assunto', 'Not informed'),
                        'classe': data.get('classe', 'Not informed'),
                        'status': CourtIntegrationService._parse_status(data.get('situacao', '')),
                        'data_distribuicao': data.get('dataDistribuicao'),
                        'valor_causa': data.get('valorCausa'),
                        'partes': CourtIntegrationService._parse_parties(data.get('partes', [])),
                        'movimentacoes': data.get('movimentacoes', []),
                        'ultima_atualizacao': data.get('dataUltimaMovimentacao'),
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Process not found in TJPR',
                    'process_number': process_number,
                    'court': 'TJPR'
                }
                
        except requests.Timeout:
            return {
                'success': False,
                'error': 'Timeout querying TJPR',
                'process_number': process_number,
                'court': 'TJPR'
            }
        except Exception as e:
            return CourtIntegrationService._get_mock_data(process_number, 'TJPR')
    
    @staticmethod
    def _search_tjsp(process_number: str) -> Dict:
        """
        Search process in TJSP (São Paulo Court of Justice)
        """
        try:
            url = f"https://esaj.tjsp.jus.br/cpopg/search.do?numeroDigitoAnoUnificado={process_number}"
            
            return CourtIntegrationService._get_mock_data(process_number, 'TJSP')
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error querying TJSP: {str(e)}',
                'process_number': process_number,
                'court': 'TJSP'
            }
    
    @staticmethod
    def _search_trt9(process_number: str) -> Dict:
        """
        Search process in TRT9 (Tribunal Regional do Trabalho 9ª Região)
        """
        try:
            return CourtIntegrationService._get_mock_data(process_number, 'TRT9')
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error querying TRT9: {str(e)}',
                'process_number': process_number,
                'court': 'TRT9'
            }
    
    @staticmethod
    def _parse_status(situacao: str) -> str:
        """
        Convert court status to internal status
        """
        situacao_lower = situacao.lower()
        
        if 'arquivado' in situacao_lower:
            return 'archived'
        elif 'suspenso' in situacao_lower:
            return 'suspended'
        elif 'encerrado' in situacao_lower or 'finalizado' in situacao_lower:
            return 'finished'
        else:
            return 'active'
    
    @staticmethod
    def _parse_parties(partes: List[Dict]) -> Dict:
        """
        Organize process parties
        """
        resultado = {
            'autores': [],
            'reus': [],
            'outros': []
        }
        
        for parte in partes:
            tipo = parte.get('tipo', '').lower()
            nome = parte.get('nome', '')
            
            if 'autor' in tipo or 'requerente' in tipo:
                resultado['autores'].append(nome)
            elif 'reu' in tipo or 'requerido' in tipo:
                resultado['reus'].append(nome)
            else:
                resultado['outros'].append(nome)
        
        return resultado
    
    @staticmethod
    def _get_mock_data(process_number: str, court: str) -> Dict:
        """
        Return mock data for testing (when API is not available)
        """
        return {
            'success': True,
            'mock': True,
            'process_number': process_number,
            'court': court,
            'message': 'Mock data - real integration in development',
            'data': {
                'numero_processo': process_number,
                'vara': f'1st Civil Court - {court}',
                'assunto': 'Mock process for testing',
                'classe': 'Common Procedure',
                'status': 'active',
                'data_distribuicao': '2024-01-15',
                'valor_causa': '50000.00',
                'partes': {
                    'autores': ['Company XYZ Ltd'],
                    'reus': ['Supplier ABC S.A.'],
                    'outros': []
                },
                'movimentacoes': [
                    {
                        'data': '2024-11-20',
                        'descricao': 'Submission of petition'
                    },
                    {
                        'data': '2024-10-15',
                        'descricao': 'Conciliation hearing held'
                    },
                    {
                        'data': '2024-09-10',
                        'descricao': 'Service performed'
                    }
                ],
                'ultima_atualizacao': '2024-11-20'
            }
        }
