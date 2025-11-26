# models/__init__.py
# 🔥 CORREÇÃO: Importação correta do DatabaseManager

try:
    from .database import Base, DatabaseManager
    # engine e SessionLocal vêm da instância singleton do DatabaseManager
    # que é inicializado em main.py via lifespan
except ImportError as e:
    print(f"⚠️ Aviso na importação: {e}")
    # Definir fallbacks
    Base = None
    DatabaseManager = None

# Importar modelos
from .clientes import Cliente, Contrato, ServicoContratado, Usuario, DashboardMetrica, Auditoria
from .contabil import DRE, ObrigacaoAcessoria
from .financeiro import LancamentoFinanceiro, IndicadorFinanceiro

__all__ = [
    'Base', 
    'DatabaseManager',
    'Cliente',
    'Contrato', 
    'ServicoContratado',
    'Usuario',
    'DashboardMetrica', 
    'Auditoria',
    'DRE', 
    'ObrigacaoAcessoria',
    'LancamentoFinanceiro', 
    'IndicadorFinanceiro'
]