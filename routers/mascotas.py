from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from entidades import Mascota, Usuario, Vacuna, Historial, Bitacora
from typing import Optional
import re

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
def dashboard(
    request: Request,
    cedula: str = Query(...),
    mascota_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, cedula)
    mascotas_usuario = session.exec(select(Mascota).where(Mascota.cedula_dueno == cedula)).all()

    mascota_activa = None
    vacunas_lista, historial_lista, bitacora_lista = [], [], []

    if mascota_id:
        mascota_activa = session.get(Mascota, mascota_id)
    elif mascotas_usuario:
        mascota_activa = mascotas_usuario[0]

    if mascota_activa:
        vacunas_lista = session.exec(select(Vacuna).where(Vacuna.id_mascota == mascota_activa.id_mascota)).all()
        historial_lista = session.exec(select(Historial).where(Historial.id_mascota == mascota_activa.id_mascota)).all()
        bitacora_lista = session.exec(select(Bitacora).where(Bitacora.id_mascota == mascota_activa.id_mascota)).all()

    return templates.TemplateResponse(request, "dashboard.html", {
        "nombre": usuario.nombre_completo if usuario else "",
        "cedula": cedula,
        "mascotas": mascotas_usuario,
        "mascota_activa": mascota_activa,
        "vacunas": vacunas_lista,
        "historial": historial_lista,
        "bitacora": bitacora_lista
    })


@router.get("/registrar-mascota")
def registrar_mascota_page(request: Request, cedula: str = Query(None)):
    return templates.TemplateResponse(request, "registrar_mascota.html", {
        "cedula_dueno": cedula or "", "errores": {}, "form": {}
    })


@router.post("/registrar-mascota")
def registrar_mascota_post(
    request: Request,
    nombre_mascota: str = Form(...),
    especie: str = Form(...),
    raza: str = Form(...),
    edad: int = Form(...),
    peso: float = Form(...),
    genero: str = Form(...),
    color: str = Form(...),
    estado_reproductivo: str = Form(...),
    cedula_dueno: str = Form(None),
    session: Session = Depends(get_session)
):
    nombre_mascota = nombre_mascota.strip()
    especie = especie.strip()
    raza = raza.strip()
    color = color.strip()

    form = {
        "nombre_mascota": nombre_mascota, "especie": especie, "raza": raza,
        "edad": edad, "peso": peso, "genero": genero, "color": color,
        "estado_reproductivo": estado_reproductivo
    }
    errores = {}

    if len(nombre_mascota) < 2:
        errores["nombre_mascota"] = "El nombre debe tener al menos 2 caracteres."
    elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre_mascota):
        errores["nombre_mascota"] = "El nombre solo puede contener letras."

    ESPECIES_VALIDAS = ["perro", "gato", "conejo", "ave"]
    if especie.lower() not in ESPECIES_VALIDAS:
        errores["especie"] = "Por favor, selecciona una especie válida de la lista."

    if len(raza) < 2:
        errores["raza"] = "Por favor, ingresa una raza válida (mínimo 2 caracteres)."

    if len(color) < 3 or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s/]+$", color):
        errores["color"] = "Por favor, ingresa un color válido (solo letras)."

    # Rangos de peso por especie (min_kg, max_kg)
    PESO_POR_ESPECIE = {
        "perro": (0.5, 120.0),
        "gato": (0.5, 15.0),
        "conejo": (0.3, 8.0),
        "ave": (0.01, 2.0),
    }

    if edad < 0 or edad > 50:
        errores["edad"] = "La edad debe estar entre 0 y 50 años."

    especie_lower = especie.strip().lower()
    if especie_lower in PESO_POR_ESPECIE:
        peso_min, peso_max = PESO_POR_ESPECIE[especie_lower]
        if peso < peso_min or peso > peso_max:
            errores["peso"] = (
                f"Para un {especie_lower}, el peso debe estar entre "
                f"{peso_min} kg y {peso_max} kg."
            )
    else:
        if peso <= 0 or peso > 500:
            errores["peso"] = "El peso debe ser mayor a 0 kg."

    if errores:
        return templates.TemplateResponse(request, "registrar_mascota.html", {
            "cedula_dueno": cedula_dueno, "errores": errores, "form": form
        })

    mascotas_existentes = session.exec(select(Mascota)).all()
    nuevo_id = len(mascotas_existentes) + 1

    mascota = Mascota(
        id_mascota=nuevo_id,
        nombre_mascota=nombre_mascota.title(),
        especie=especie.title(),
        raza=raza.title(),
        edad=edad,
        peso=peso,
        genero=genero,
        color=color.title(),
        estado_reproductivo=estado_reproductivo,
        cedula_dueno=cedula_dueno
    )
    session.add(mascota)
    session.commit()

    mascotas_usuario = session.exec(select(Mascota).where(Mascota.cedula_dueno == cedula_dueno)).all()
    usuario = session.get(Usuario, cedula_dueno)

    return templates.TemplateResponse(request, "dashboard.html", {
        "nombre": usuario.nombre_completo if usuario else "",
        "cedula": cedula_dueno,
        "mascotas": mascotas_usuario,
        "mascota_activa": mascota,
        "vacunas": [], "historial": [], "bitacora": []
    })