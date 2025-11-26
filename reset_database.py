import os
import sys
from pathlib import Path

def reset_completo():
    """Limpeza completa do banco e cache"""
    print("🧹 LIMPEZA COMPLETA INICIADA...")
    
    # 1. Deletar arquivo do banco
    db_path = Path("backend/database/contabiliza_ia.db")
    if db_path.exists():
        db_path.unlink()
        print("✅ Banco de dados deletado")
    
    # 2. Limpar cache do Python
    cache_dirs = [
        "__pycache__",
        "backend/__pycache__",
        "backend/app/__pycache__", 
        "backend/app/models/__pycache__",
        "backend/app/routes/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            import shutil
            shutil.rmtree(cache_path)
            print(f"✅ Cache removido: {cache_dir}")
    
    print("🎯 Agora execute: python run.py")

if __name__ == "__main__":
    reset_completo()