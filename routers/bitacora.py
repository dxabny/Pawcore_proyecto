from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from entidades import Bitacora
from utils import parsear_fecha, EVENTOS_VALIDOS

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.post("/agregar-bitacora")
def admin_agregar_bitacora(
    request: Request,
    id_mascota: int = Form(...),
    fecha: str = Form(...),
    tipo_evento: str = Form(...),
    motivo: str = Form(...),
    sintomas: str = Form(...),
    diagnostico: str = Form(...),
    procedimiento: str = Form(...),
    medicacion: str = Form("Ninguna"),
    observaciones: str = Form(...),
    session: Session = Depends(get_session)
):
    from routers.admin_dashboard import admin_dashboard_ver_detalle

    errores = {}
    fecha_obj = parsear_fecha(fecha)
    if not fecha_obj:
        errores["bitacora"] = "Fecha inválida. Usa el formato DD/MM/AAAA."

    if tipo_evento not in EVENTOS_VALIDOS:
        errores["bitacora"] = f"Tipo de evento no válido. Opciones: {', '.join(EVENTOS_VALIDOS)}."

    if len(motivo.strip()) < 5:
        errores["bitacora_campos"] = "El motivo de la consulta debe tener al menos 5 caracteres."
    if len(diagnostico.strip()) < 3:
        errores["bitacora_campos"] = "El diagnóstico médico es obligatorio."
    if len(procedimiento.strip()) < 3:
        errores["bitacora_campos"] = "El procedimiento realizado es obligatorio."
    if len(observaciones.strip()) < 3:
        errores["bitacora_campos"] = "Las observaciones son obligatorias."

    if errores:
        return admin_dashboard_ver_detalle(request, mascota_id=id_mascota, errores_admin=errores, session=session)

    b = Bitacora(
        fecha=fecha_obj,
        tipo_evento=tipo_evento,
        motivo=motivo.strip(),
        sintomas=sintomas.strip(),
        diagnostico=diagnostico.strip(),
        procedimiento=procedimiento.strip(),
        medicacion=medicacion.strip() or "Ninguna",
        observaciones=observaciones.strip(),
        id_mascota=id_mascota
    )
    session.add(b)
    session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}#bitacora", status_code=303)


@router.get("/actualizar-bitacora/{id_bitacora}")
def admin_actualizar_bitacora_page(
    request: Request,
    id_bitacora: int,
    id_mascota: int = Query(...),
    session: Session = Depends(get_session)
):
    b = session.get(Bitacora, id_bitacora)
    if not b:
        raise HTTPException(status_code=404, detail="Registro de bitácora no encontrado.")
    return templates.TemplateResponse(request, "actualizar_bitacora.html", {
        "b": b, "id_mascota": id_mascota, "errores": {}
    })


@router.post("/actualizar-bitacora/{id_bitacora}")
def admin_actualizar_bitacora_post(
    request: Request,
    id_bitacora: int,
    id_mascota: int = Form(...),
    fecha: str = Form(...),
    tipo_evento: str = Form(...),
    motivo: str = Form(...),
    sintomas: str = Form(...),
    diagnostico: str = Form(...),
    procedimiento: str = Form(...),
    medicacion: str = Form("Ninguna"),
    observaciones: str = Form(...),
    session: Session = Depends(get_session)
):
    errores = {}
    fecha_obj = parsear_fecha(fecha)
    if not fecha_obj:
        errores["bitacora"] = "Fecha inválida. Usa el formato DD/MM/AAAA."

    if tipo_evento not in EVENTOS_VALIDOS:
        errores["bitacora"] = "Tipo de evento no válido."

    if len(motivo.strip()) < 5:
        errores["bitacora_campos"] = "El motivo debe tener al menos 5 caracteres."
    if len(diagnostico.strip()) < 3:
        errores["bitacora_campos"] = "El diagnóstico es obligatorio."

    b = session.get(Bitacora, id_bitacora)
    if not b:
        raise HTTPException(status_code=404, detail="Registro de bitácora no encontrado.")

    if errores:
        return templates.TemplateResponse(request, "actualizar_bitacora.html", {
            "b": b, "id_mascota": id_mascota, "errores": errores
        })

    b.fecha = fecha_obj
    b.tipo_evento = tipo_evento
    b.motivo = motivo.strip()
    b.sintomas = sintomas.strip()
    b.diagnostico = diagnostico.strip()
    b.procedimiento = procedimiento.strip()
    b.medicacion = medicacion.strip() or "Ninguna"
    b.observaciones = observaciones.strip()
    session.add(b)
    session.commit()
    return RedirectResponse(f"/admin/dashboard?mascota_id={id_mascota}#bitacora", status_code=303)