import sys
import os
from sqlalchemy import text  # ← ADICIONE ESTA LINHA

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.database import DatabaseManager

def verificar_tabelas():
    print("🔍 Verificando tabelas do banco...")
    
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        # Use text() para queries SQL
        result = session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
        tables = [row[0] for row in result]
        
        print(f"🎯 {len(tables)} TABELAS CRIADAS:")
        for table in tables:
            print(f"   📋 {table}")
            
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        db.fechar_sessao(session)

if __name__ == "__main__":
    verificar_tabelas()