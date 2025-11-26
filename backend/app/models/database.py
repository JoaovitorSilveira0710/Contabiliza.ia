from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Base para todos os models
Base = declarative_base()

class DatabaseManager:
    def __init__(self, database_url: str = None):
        # 🔥 CORREÇÃO: Caminho correto para o banco
        # Estamos em: backend/app/models/database.py
        # Queremos: backend/database/contabiliza_ia.db
        project_root = Path(__file__).absolute().parent.parent.parent  # backend/
        self.DB_DIR = project_root / "database"  # backend/database/
        
        # Garantir que a pasta database existe
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Caminho do banco
        db_path = self.DB_DIR / "contabiliza_ia.db"
        self.database_url = f"sqlite:///{db_path}"
        
        logger.info(f"🎯 CAMINHO CORRIGIDO DO BANCO:")
        logger.info(f"   📁 Pasta: {self.DB_DIR}")
        logger.info(f"   🗄️ Arquivo: {db_path}")
        logger.info(f"   🔗 URL: {self.database_url}")
        
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_engine(self):
        """Cria engine do SQLAlchemy com configurações otimizadas"""
        engine_kwargs = {
            "echo": False,
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "connect_args": {"check_same_thread": False}
        }

        logger.info("🔧 Criando engine do SQLAlchemy...")
        return create_engine(self.database_url, **engine_kwargs)

    def _importar_modelos(self):
        """Importa todos os modelos - VERSÃO SIMPLIFICADA"""
        try:
            logger.info("📦 Importando modelos...")
            
            # 🔥 CORREÇÃO: Importar diretamente os modelos que corrigimos
            from . import clientes
            logger.info("✅ clientes.py importado")
            
            from . import contabil
            logger.info("✅ contabil.py importado")
            
            from . import financeiro
            logger.info("✅ financeiro.py importado")
            
            from . import juridico
            logger.info("✅ juridico.py importado")
            
            # 🔥 CORREÇÃO: notas_fiscais em vez de notas
            from . import notas_fiscais
            logger.info("✅ notas_fiscais.py importado")
            
            logger.info("🎯 Todos os modelos importados com sucesso!")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao importar modelos: {e}")
            return False

    def criar_tabelas(self):
        """Cria todas as tabelas no banco de dados - VERSÃO SIMPLIFICADA"""
        try:
            logger.info("🛠️ Criando tabelas...")
            
            # Importar modelos primeiro
            if not self._importar_modelos():
                logger.error("❌ Falha ao importar modelos")
                return False
            
            # 🔥 CORREÇÃO: Criar tabelas SEM dropar (para desenvolvimento)
            environment = os.getenv("ENVIRONMENT", "development")
            if environment.lower() in ["development", "dev"]:
                try:
                    # Apenas dropar se especificamente necessário
                    drop_tables = os.getenv("DROP_TABLES", "false").lower() == "true"
                    if drop_tables:
                        Base.metadata.drop_all(bind=self.engine)
                        logger.info("🗑️ Tabelas antigas removidas")
                except Exception as e:
                    logger.warning(f"⚠️ Erro na limpeza: {e}")
            
            # Criar tabelas
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Tabelas criadas com sucesso!")

            # Verificar criação
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"📊 {len(tables)} tabelas criadas: {tables}")
            
            # Verificar se arquivo foi criado
            db_file = self.DB_DIR / "contabiliza_ia.db"
            if db_file.exists():
                logger.info(f"🎉 BANCO CRIADO: {db_file}")
                return True
            else:
                logger.error(f"💥 Banco não encontrado em: {db_file}")
                return False

        except Exception as e:
            logger.exception(f"❌ Erro ao criar tabelas: {e}")
            return False

    def get_session(self):
        """Retorna uma nova sessão do banco de dados"""
        return self.SessionLocal()

    def fechar_sessao(self, session):
        """Fecha uma sessão do banco de dados"""
        try:
            session.close()
        except Exception:
            pass

    def testar_conexao(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("✅ Conexão estabelecida")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            return False

    def get_database_info(self) -> dict:
        """Retorna informações sobre o banco de dados"""
        db_file = self.DB_DIR / "contabiliza_ia.db"
        return {
            "database_url": self.database_url,
            "expected_path": str(db_file),
            "file_exists": db_file.exists(),
            "file_size": db_file.stat().st_size if db_file.exists() else 0,
            "tables": self._listar_tabelas() if self.testar_conexao() else []
        }

    def _listar_tabelas(self):
        """Lista todas as tabelas do banco"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception:
            return []

# Instância global
db_manager = DatabaseManager()

def get_db():
    """Dependency para FastAPI"""
    db = db_manager.get_session()
    try:
        yield db
    except Exception as e:
        logger.error(f"❌ Erro na sessão: {e}")
        db.rollback()
        raise
    finally:
        db_manager.fechar_sessao(db)

def inicializar_banco_dados():
    """Função principal para inicializar o banco de dados"""
    logger.info("🚀 Inicializando banco de dados...")
    
    # Mostrar info antes
    info = db_manager.get_database_info()
    logger.info(f"🎯 Esperado em: {info['expected_path']}")
    
    if not db_manager.testar_conexao():
        logger.error("❌ Falha na conexão")
        return False
    
    try:
        success = db_manager.criar_tabelas()
        if success:
            # Verificação final
            final_info = db_manager.get_database_info()
            if final_info['file_exists']:
                logger.info(f"🎉 SUCESSO! Banco criado em: {final_info['expected_path']}")
                logger.info(f"📊 Tabelas: {final_info['tables']}")
            else:
                logger.error("💥 Banco não foi criado no local esperado!")
            return success
        else:
            logger.error("❌ Falha ao criar tabelas")
            return False
    except Exception as e:
        logger.error(f"❌ Falha na inicialização: {e}")
        return False

if __name__ == "__main__":
    success = inicializar_banco_dados()
    if not success:
        exit(1)