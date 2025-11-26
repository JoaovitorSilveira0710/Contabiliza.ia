import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

# inicialização do DB/manager
from backend.app.models.database import inicializar_banco_dados, db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.app.main")

# Lifespan manager: inicializa banco na startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Aplicação iniciando: inicializando banco de dados...")
    try:
        inicializar_banco_dados()
    except Exception as e:
        logger.error(f"❌ Falha ao inicializar banco de dados: {e}")
    yield
    logger.info("⏹️ Aplicação finalizando...")

app = FastAPI(
    title="Contabiliza.IA - API",
    description="API backend do Contabiliza.IA",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS (desenvolvimento)
_allowed_origins = os.getenv("FRONTEND_ORIGINS", "*")
if _allowed_origins == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in _allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers (try/except para não quebrar se faltar arquivo)
routers = []
try:
    from backend.app.routes.clientes import router as clientes_router
    routers.append(("clientes", clientes_router))
except Exception as e:
    logger.info(f"Router clientes não importado: {e}")

try:
    from backend.app.routes.auth import router as auth_router
    routers.append(("auth", auth_router))
except Exception as e:
    logger.info(f"Router auth não importado: {e}")

try:
    from backend.app.routes.financeiro import router as financeiro_router
    routers.append(("financeiro", financeiro_router))
except Exception as e:
    logger.info(f"Router financeiro não importado: {e}")

try:
    from backend.app.routes.contabil import router as contabil_router
    routers.append(("contabil", contabil_router))
except Exception as e:
    logger.info(f"Router contabil não importado: {e}")

try:
    from backend.app.routes.notas_fiscais import router as notas_fiscais_router
    routers.append(("notas_fiscais", notas_fiscais_router))
except Exception as e:
    logger.info(f"Router notas_fiscais não importado: {e}")

try:
    from backend.app.routes.juridico import router as juridico_router
    routers.append(("juridico", juridico_router))
except Exception as e:
    logger.info(f"Router juridico não importado: {e}")

try:
    from backend.app.routes.dashboard import router as dashboard_router
    routers.append(("dashboard", dashboard_router))
except Exception as e:
    logger.info(f"Router dashboard não importado: {e}")

# Incluir routers com prefix /api (faça isso antes de montar o frontend estático)
for name, r in routers:
    try:
        app.include_router(r, prefix="/api")
        logger.info(f"✅ Router incluído em /api{getattr(r, 'prefix', '')}")
    except Exception as e:
        logger.error(f"❌ Erro ao incluir router {name}: {e}")

# Montar frontend estático somente após incluir as rotas da API
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    logger.info(f"📦 Montando frontend estático em: {FRONTEND_DIR}")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    logger.info("📦 Pasta frontend não encontrada — nenhuma rota estática montada")

# Handler de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Health check
@app.get("/health", tags=["health"])
async def health():
    ok = False
    try:
        ok = db_manager.testar_conexao()
    except Exception:
        ok = False
    return {"status": "ok" if ok else "error"}