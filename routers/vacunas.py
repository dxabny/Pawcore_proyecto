from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from entidades import Vacuna
from utils import parsear_fecha
import re

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.post("/agregar-vacuna")
def admin_agregar_vacuna(
    request: Request,
    id_mascota: int = Form(...),
    nombre_vacuna: str = Form(...),
    fecha_aplicacion: str = Form(...),
    proxima_dosis: str = Form(...),
    session: Session = Depends(get_session)
):
    from routers.admin_dashboard import admin_dashboard_ver_detalle

    nombre_vacuna = nombre_vacuna.strip()
    errores = {}

    if len(nombre_vacuna) < 2:
        errores["vacuna"] = "El nombre de la vacuna es obligatorio (mínimo 2 caracteres)."
    elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-]+$", nombre_vacuna):
        errores["vacuna"] = "El nombre de la vacuna solo puede contener letras, números y guiones."

    f_app = parsear_fecha(fecha_aplicacion)
    f_prox = parsear_fecha(proxima_dosis)

    if not f_app:
        errores["fecha_vacuna"] = "Fecha de aplicación inválida. Usa el formato DD/MM/AAAA."
    if not f_prox:
        errores["fecha_vacuna"] = "Fecha de próxima dosis inválida. Usa el formato DD/MM/AAAA."
    if f_app and f_prox and f_prox <= f_app:
        errores["fecha_vacuna"] = "La próxima dosis debe ser posterior a la fecha de aplicación."

    if errores:
        return admin_dashboard_ver_detalle(request, mascota_id=id_mascota, errores_admin=errores, session=session)

    vacuna = Vacuna(
        nombre_vacuna=nombre_vacuna.title(),
        fecha_aplicacion=f_app,
        proxima_dosis=f_prox,
        id_mascota=id_mascota
    )
    session.add(vacuna)
    session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}#vacunas", status_code=303)


@router.post("/eliminar-vacuna/{id_vacuna}")
def admin_eliminar_vacuna(
    id_vacuna: int,
    id_mascota: int = Form(...),
    session: Session = Depends(get_session)
):
    v = session.get(Vacuna, id_vacuna)
    if v:
        session.delete(v)
        session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}", status_code=303)


@router.get("/actualizar-vacuna/{id_vacuna}")
def admin_actualizar_vacuna_page(
    request: Request,
    id_vacuna: int,
    id_mascota: int = Query(...),
    session: Session = Depends(get_session)
):
    v = session.get(Vacuna, id_vacuna)
    if not v:
        raise HTTPException(status_code=404, detail="Vacuna no encontrada.")
    return templates.TemplateResponse(request, "actualizar_vacuna.html", {
        "v": v, "id_mascota": id_mascota, "errores": {}
    })


@router.post("/actualizar-vacuna/{id_vacuna}")
def admin_actualizar_vacuna_post(
    request: Request,
    id_vacuna: int,
    id_mascota: int = Form(...),
    nombre_vacuna: str = Form(...),
    fecha_aplicacion: str = Form(...),
    proxima_dosis: str = Form(...),
    session: Session = Depends(get_session)
):
    nombre_vacuna = nombre_vacuna.strip()
    errores = {}

    if len(nombre_vacuna) < 2:
        errores["vacuna"] = "El nombre de la vacuna es obligatorio (mínimo 2 caracteres)."
    elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-]+$", nombre_vacuna):
        errores["vacuna"] = "El nombre solo puede contener letras, números y guiones."

    f_app = parsear_fecha(fecha_aplicacion)
    f_prox = parsear_fecha(proxima_dosis)

    if not f_app:
        errores["fecha_vacuna"] = "Fecha de aplicación inválida. Usa DD/MM/AAAA."
    if not f_prox:
        errores["fecha_vacuna"] = "Fecha de próxima dosis inválida. Usa DD/MM/AAAA."
    if f_app and f_prox and f_prox <= f_app:
        errores["fecha_vacuna"] = "La próxima dosis debe ser posterior a la fecha de aplicación."

    v = session.get(Vacuna, id_vacuna)
    if not v:
        raise HTTPException(status_code=404, detail="Vacuna no encontrada.")

    if errores:
        return templates.TemplateResponse(request, "actualizar_vacuna.html", {
            "v": v, "id_mascota": id_mascota, "errores": errores
        })

    v.nombre_vacuna = nombre_vacuna.title()
    v.fecha_aplicacion = f_app
    v.proxima_dosis = f_prox
    session.add(v)
    session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}#vacunas", status_code=303)