from fastapi import APIRouter

router = APIRouter(prefix="/notas", tags=["notas"])

@router.get("/", summary="Listar notas (placeholder)")
async def listar_notas():
    return {"notas": [], "message": "rota placeholder - implemente quando necessário"}