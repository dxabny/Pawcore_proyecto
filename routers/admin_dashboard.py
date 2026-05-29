from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from entidades import Mascota, Usuario, Vacuna, Historial, Bitacora
from typing import Optional
from collections import Counter

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
def admin_dashboard_ver_detalle(
    request: Request,
    mascota_id: Optional[int] = Query(None),
    buscar: Optional[str] = Query(None),
    errores_admin: Optional[dict] = None,
    session: Session = Depends(get_session)
):
    mascotas_todas = session.exec(select(Mascota)).all()
    mascota_seleccionada = None
    dueno = None
    vacunas_lista, historial_lista, bitacora_lista = [], [], []

    if buscar:
        buscar_limpio = buscar.strip().replace("#", "")
        mascotas_filtradas = []
        if buscar_limpio.isdigit():
            for m in mascotas_todas:
                if int(buscar_limpio) == m.id_mascota:
                    mascotas_filtradas.append(m)
        else:
            for m in mascotas_todas:
                if m.cedula_dueno and buscar_limpio in m.cedula_dueno:
                    mascotas_filtradas.append(m)
        if len(mascotas_filtradas) == 1 and not mascota_id:
            mascota_id = mascotas_filtradas[0].id_mascota
    else:
        mascotas_filtradas = mascotas_todas

    if mascota_id:
        mascota_seleccionada = session.get(Mascota, mascota_id)

    if mascota_seleccionada:
        dueno = session.get(Usuario, mascota_seleccionada.cedula_dueno)
        vacunas_lista = session.exec(select(Vacuna).where(Vacuna.id_mascota == mascota_seleccionada.id_mascota)).all()
        historial_lista = session.exec(select(Historial).where(Historial.id_mascota == mascota_seleccionada.id_mascota)).all()
        bitacora_lista = session.exec(select(Bitacora).where(Bitacora.id_mascota == mascota_seleccionada.id_mascota)).all()

    total_vacunas = len(session.exec(select(Vacuna)).all())
    total_historiales = len(session.exec(select(Historial)).all())

    todas_bitacoras = session.exec(select(Bitacora)).all()
    especies_count = Counter(m.especie for m in mascotas_todas)
    genero_count = Counter(m.genero for m in mascotas_todas)
    eventos_count = Counter(b.tipo_evento for b in todas_bitacoras)
    total_consultas = len(todas_bitacoras)

    return templates.TemplateResponse(request, "admin_dashboard.html", {
        "mascotas": mascotas_filtradas,
        "mascotas_todas": mascotas_todas,
        "total_vacunas": total_vacunas,
        "total_historiales": total_historiales,
        "mascota_activa": mascota_seleccionada,
        "dueno": dueno,
        "vacunas": vacunas_lista,
        "historial": historial_lista,
        "bitacora": bitacora_lista,
        "buscar": buscar,
        "errores_admin": errores_admin or {},
        "chart_especies_labels": list(especies_count.keys()),
        "chart_especies_data": list(especies_count.values()),
        "chart_genero_labels": list(genero_count.keys()),
        "chart_genero_data": list(genero_count.values()),
        "chart_eventos_labels": list(eventos_count.keys()),
        "chart_eventos_data": list(eventos_count.values()),
        "total_consultas": total_consultas,
    })