from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from entidades import Historial
from utils import parsear_fecha

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.post("/agregar-historial")
def admin_agregar_historial(
    request: Request,
    id_mascota: int = Form(...),
    fecha: str = Form(...),
    enfermedades_previas: str = Form("Ninguna"),
    cirugias_previas: str = Form("Ninguna"),
    alergias: str = Form("Ninguna"),
    tratamientos_previos: str = Form("Ninguno"),
    session: Session = Depends(get_session)
):
    from routers.admin_dashboard import admin_dashboard_ver_detalle

    errores = {}
    fecha_obj = parsear_fecha(fecha)
    if not fecha_obj:
        errores["fecha_historial"] = "Fecha inválida. Usa el formato DD/MM/AAAA."

    enfermedades_previas = enfermedades_previas.strip() or "Ninguna"
    cirugias_previas = cirugias_previas.strip() or "Ninguna"
    alergias = alergias.strip() or "Ninguna"
    tratamientos_previos = tratamientos_previos.strip() or "Ninguno"

    if errores:
        return admin_dashboard_ver_detalle(request, mascota_id=id_mascota, errores_admin=errores, session=session)

    h = Historial(
        fecha=fecha_obj,
        enfermedades_previas=enfermedades_previas,
        cirugias_previas=cirugias_previas,
        alergias=alergias,
        tratamientos_previos=tratamientos_previos,
        id_mascota=id_mascota
    )
    session.add(h)
    session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}#historial", status_code=303)


@router.get("/editar-historial/{id_historial}")
def admin_editar_historial_page(
    request: Request,
    id_historial: int,
    id_mascota: int = Query(...),
    session: Session = Depends(get_session)
):
    h = session.get(Historial, id_historial)
    if not h:
        raise HTTPException(status_code=404, detail="Historial no encontrado.")
    return templates.TemplateResponse(request, "editar_historial.html", {
        "h": h, "id_mascota": id_mascota, "errores": {}
    })


@router.post("/editar-historial/{id_historial}")
def admin_editar_historial_post(
    request: Request,
    id_historial: int,
    id_mascota: int = Form(...),
    fecha: str = Form(...),
    enfermedades_previas: str = Form("Ninguna"),
    cirugias_previas: str = Form("Ninguna"),
    alergias: str = Form("Ninguna"),
    tratamientos_previos: str = Form("Ninguno"),
    session: Session = Depends(get_session)
):
    errores = {}
    fecha_obj = parsear_fecha(fecha)
    if not fecha_obj:
        errores["fecha_historial"] = "Fecha inválida. Usa el formato DD/MM/AAAA."

    h = session.get(Historial, id_historial)
    if not h:
        raise HTTPException(status_code=404, detail="Historial no encontrado.")

    if errores:
        return templates.TemplateResponse(request, "editar_historial.html", {
            "h": h, "id_mascota": id_mascota, "errores": errores
        })

    h.fecha = fecha_obj
    h.enfermedades_previas = enfermedades_previas.strip() or "Ninguna"
    h.cirugias_previas = cirugias_previas.strip() or "Ninguna"
    h.alergias = alergias.strip() or "Ninguna"
    h.tratamientos_previos = tratamientos_previos.strip() or "Ninguno"
    session.add(h)
    session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}#historial", status_code=303)