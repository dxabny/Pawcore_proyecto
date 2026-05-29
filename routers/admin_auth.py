from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from entidades import Admin

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "admin_login.html", {"error": None})


@router.post("/login")
def admin_login_post(
    request: Request,
    usuario: str = Form(...),
    contrasena: str = Form(...),
    session: Session = Depends(get_session)
):
    usuario = usuario.strip()
    contrasena = contrasena.strip()

    if not usuario or not contrasena:
        return templates.TemplateResponse(request, "admin_login.html", {
            "error": "Usuario y contraseña son obligatorios."
        })

    admin = session.exec(select(Admin).where(Admin.usuario == usuario, Admin.contrasena == contrasena)).first()
    if not admin:
        return templates.TemplateResponse(request, "admin_login.html", {
            "error": "Usuario o contraseña incorrectos."
        })

    return RedirectResponse("/admin/dashboard", status_code=303)