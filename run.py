# run.py - Coloque na raiz do seu projeto (mesmo nível de backend/)
import os
import sys
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run")

def main():
    try:
        logger.info("🚀 Iniciando Contabiliza.IA...")
        
        # Verificar se estamos no diretório correto
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.join(current_dir, "backend")
        
        if not os.path.exists(backend_dir):
            logger.error("❌ Diretório 'backend' não encontrado!")
            logger.info("💡 Execute este script da raiz do projeto")
            return
        
        logger.info(f"📁 Diretório do projeto: {current_dir}")
        
        # Iniciar servidor
        logger.info("🌐 Iniciando servidor FastAPI...")
        logger.info("📚 Docs disponíveis em: http://localhost:8000/docs")
        logger.info("🏥 Health check em: http://localhost:8000/health")
        
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()