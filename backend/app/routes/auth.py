from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginData(BaseModel):
    email: str
    senha: str


@router.post("/login")
async def login(data: LoginData):
    """Simple development login endpoint.

    This is intentionally minimal: it accepts any credentials and returns a
    dummy token plus a small user object so the frontend can proceed during
    local development. Replace with real auth in production.
    """
    # In a real app validate credentials here. We'll accept any non-empty.
    if not data.email or not data.senha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email e senha são obrigatórios")

    token = "dev-token"
    user = {"email": data.email, "name": data.email.split("@")[0]}

    return {"token": token, "user": user}


@router.get("/me")
async def me(request: Request):
    """Return a small user object when a valid dev token is presented."""
    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = auth.split()[1]
    if token != "dev-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # For development we return a simple user payload
    return {"email": "dev@local", "name": "dev", "roles": ["admin"]}
