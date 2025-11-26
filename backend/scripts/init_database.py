import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.database import DatabaseManager, Base
from app.models.clientes import Cliente, Contrato
from app.models.financeiro import LancamentoFinanceiro
from app.models.contabil import DRE, ObrigacaoAcessoria
from app.models.juridico import Processo
from app.models.notas_fiscais import NotaFiscal
from datetime import date

def popular_dados_exemplo(db_manager):
    """Insere dados de exemplo para testes"""
    session = db_manager.get_session()
    
    try:
        # Clientes de exemplo
        cliente1 = Cliente(
            nome_razao_social="Empresa Exemplo Ltda",
            cnpj_cpf="12.345.678/0001-90",
            email="contato@empresaexemplo.com",
            telefone="(11) 99999-9999",
            endereco="Rua Exemplo, 123 - São Paulo/SP",
            tipo_pessoa="J",
            ativo=True
        )
        
        cliente2 = Cliente(
            nome_razao_social="Consultoria XYZ ME",
            cnpj_cpf="98.765.432/0001-10", 
            email="contato@consultoriaxyz.com",
            telefone="(11) 88888-8888",
            endereco="Av. Teste, 456 - Rio de Janeiro/RJ",
            tipo_pessoa="J",
            ativo=True
        )
        
        session.add_all([cliente1, cliente2])
        session.commit()
        
        # Contratos de exemplo - USANDO date() em vez de strings
        contrato1 = Contrato(
            cliente_id=cliente1.id,
            tipo_servico="contabil",
            valor_mensal=1500.00,  # ← Float, não string
            data_inicio=date(2024, 1, 1),  # ← date object
            status="ativo"
        )
        
        session.add(contrato1)
        session.commit()
        
        print(f"✅ {session.query(Cliente).count()} clientes criados")
        print(f"✅ {session.query(Contrato).count()} contratos criados")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao popular dados: {e}")
        import traceback
        traceback.print_exc()  # ← Mostra detalhes do erro
    finally:
        db_manager.fechar_sessao(session)
def criar_banco_dados():
    print("🔄 Inicializando banco de dados do Contabiliza.IA...")
    
    try:
        # Criar gerenciador do banco
        db_manager = DatabaseManager()
        
        # Criar todas as tabelas
        db_manager.criar_tabelas()
        print("✅ Tabelas criadas com sucesso!")
        
        # Popular com dados de exemplo
        popular_dados_exemplo(db_manager)
        print("✅ Dados de exemplo inseridos!")
        
        print("🎉 Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")

def popular_dados_exemplo(db_manager):
    """Insere dados de exemplo para testes"""
    session = db_manager.get_session()
    
    try:
        # Clientes de exemplo
        cliente1 = Cliente(
            nome_razao_social="Empresa Exemplo Ltda",
            cnpj_cpf="12.345.678/0001-90",
            email="contato@empresaexemplo.com",
            telefone="(11) 99999-9999",
            endereco="Rua Exemplo, 123 - São Paulo/SP",
            tipo_pessoa="J",
            ativo=True
        )
        
        cliente2 = Cliente(
            nome_razao_social="Consultoria XYZ ME",
            cnpj_cpf="98.765.432/0001-10", 
            email="contato@consultoriaxyz.com",
            telefone="(11) 88888-8888",
            endereco="Av. Teste, 456 - Rio de Janeiro/RJ",
            tipo_pessoa="J",
            ativo=True
        )
        
        session.add_all([cliente1, cliente2])
        session.commit()
        
        # Contratos de exemplo
        contrato1 = Contrato(
            cliente_id=cliente1.id,
            tipo_servico="contabil",
            valor_mensal="1500.00",
            data_inicio="2024-01-01",
            status="ativo"
        )
        
        session.add(contrato1)
        session.commit()
        
        print(f"✅ {session.query(Cliente).count()} clientes criados")
        print(f"✅ {session.query(Contrato).count()} contratos criados")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao popular dados: {e}")
    finally:
        db_manager.fechar_sessao(session)

if __name__ == "__main__":
    criar_banco_dados()