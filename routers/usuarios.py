from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from entidades import Usuario, Mascota, Vacuna, Historial, Bitacora
from typing import Optional
import re
 
router = APIRouter()
templates = Jinja2Templates(directory="templates")
 
 
@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "pawcore_landing.html", {})
 
 
@router.get("/registro")
def registro_page(request: Request):
    return templates.TemplateResponse(request, "registro.html", {"errores": {}, "form": {}})
 
 
@router.post("/registro")
def registro_post(
    request: Request,
    cedula: str = Form(...),
    nombre_completo: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    session: Session = Depends(get_session)
):
    cedula = cedula.strip()
    nombre_completo = nombre_completo.strip()
    correo = correo.strip()
    telefono = telefono.strip()
    direccion = direccion.strip()
 
    form = {
        "cedula": cedula, "nombre_completo": nombre_completo,
        "correo": correo, "telefono": telefono, "direccion": direccion
    }
    errores = {}
 
    # Validar cédula
    if not cedula.isdigit():
        errores["cedula"] = "La cédula solo puede contener números."
    elif len(cedula) < 5 or len(cedula) > 15:
        errores["cedula"] = "La cédula debe tener entre 5 y 15 dígitos."
    elif session.get(Usuario, cedula):
        errores["cedula"] = "Ya existe una cuenta registrada con esa cédula."
 
    # Validar nombre
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+(?:\s+[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)+$", nombre_completo):
        errores["nombre_completo"] = "Debes ingresar nombre y apellido (solo letras)."
 
    # Validar correo
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", correo):
        errores["correo"] = "El correo no tiene un formato válido."
    else:
        if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
            errores["correo"] = "Este correo ya está registrado."
 
    # Validar teléfono
    if not telefono.isdigit():
        errores["telefono"] = "El teléfono solo puede contener números."
    elif len(telefono) < 7 or len(telefono) > 15:
        errores["telefono"] = "El teléfono debe tener entre 7 y 15 dígitos."
    elif len(set(telefono)) <= 2:
        errores["telefono"] = "El teléfono ingresado no parece real (ej: 11111111 no es válido)."
    elif telefono in ("1234567", "12345678", "123456789", "1234567890", "0987654321", "9876543210"):
        errores["telefono"] = "Por favor ingresa un número de teléfono real."
    elif re.match(r"^(\d)\1{6,}$", telefono):
        errores["telefono"] = "El teléfono no puede ser un número repetido."
    else:
        if session.exec(select(Usuario).where(Usuario.telefono == telefono)).first():
            errores["telefono"] = "Este número de teléfono ya está registrado."
 
    # Validar dirección
    PALABRAS_INVALIDAS_DIRECCION = [
        "al lado", "cerca de", "frente a", "detrás de", "por ahí", "esquina de",
        "la casa de", "el edificio de", "no sé", "no se", "cualquiera", "ninguna",
        "mi casa", "mi barrio", "allá", "acá", "aquí", "ahí", "ahi",
        "la dirección de", "la direccion de"
    ]
 
    def _es_texto_incoherente(texto):
        consonantes_seguidas = re.findall(r"[bcdfghjklmnñpqrstvwxyzBCDFGHJKLMNÑPQRSTVWXYZ]{4,}", texto)
        if consonantes_seguidas:
            return True
        if re.search(r"(.)\1{3,}", texto):
            return True
        texto_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚ]", "", texto)
        if len(texto_limpio) > 6:
            vocales = len(re.findall(r"[aeiouáéíóúAEIOUÁÉÍÓÚ]", texto_limpio))
            ratio = vocales / len(texto_limpio)
            if ratio < 0.15:
                return True
        return False
 
    if len(direccion) < 8:
        errores["direccion"] = "La dirección es muy corta (mínimo 8 caracteres)."
    elif _es_texto_incoherente(direccion):
        errores["direccion"] = "La dirección no parece válida. Ingresa una dirección real (ej: Calle 45 #12-30, Bogotá)."
    elif not re.search(r"\d", direccion):
        errores["direccion"] = "La dirección debe incluir un número (ej: Calle 45 #12-30)."
    elif any(p in direccion.lower() for p in PALABRAS_INVALIDAS_DIRECCION):
        errores["direccion"] = "Por favor ingresa una dirección real y completa (ej: Calle 45 #12-30, Bogotá)."
    elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s].*\d", direccion):
        errores["direccion"] = "La dirección debe empezar con el nombre de la vía seguido de un número (ej: Cra 7 #45-10)."
 
    # Validar contraseña
    CONTRASENAS_DEBILES = {
        "123456", "1234567", "12345678", "123456789", "1234567890",
        "password", "contraseña", "qwerty", "abc123", "111111",
        "000000", "654321", "pass123", "admin123", "letmein",
        "welcome", "monkey", "dragon", "master", "123123",
        "112233", "password1", "pawcore", "mascota123"
    }
    if len(password) < 8:
        errores["password"] = "La contraseña debe tener al menos 8 caracteres."
    elif password.lower() in CONTRASENAS_DEBILES:
        errores["password"] = "Esa contraseña es demasiado común. Elige una más segura."
    elif not re.search(r"[A-Z]", password):
        errores["password"] = "La contraseña debe incluir al menos una letra mayúscula."
    elif not re.search(r"[0-9]", password):
        errores["password"] = "La contraseña debe incluir al menos un número."
    elif not re.search(r"[^a-zA-Z0-9]", password):
        errores["password"] = "La contraseña debe incluir al menos un carácter especial (ej: @, #, !)."
    elif re.match(r"^(.)\1+$", password):
        errores["password"] = "La contraseña no puede ser un carácter repetido."
    elif password != password_confirm:
        errores["password"] = "Las contraseñas no coinciden."
 
    if errores:
        return templates.TemplateResponse(request, "registro.html", {"errores": errores, "form": form})
 
    usuario = Usuario(
        cedula=cedula, nombre_completo=nombre_completo, correo=correo,
        telefono=telefono, direccion=direccion, password=password
    )
    session.add(usuario)
    session.commit()
    return templates.TemplateResponse(request, "registrar_mascota.html", {
        "cedula_dueno": cedula, "errores": {}, "form": {}
    })
 
 
@router.get("/login")
def login_page(request: Request, recuperado: Optional[str] = Query(None)):
    return templates.TemplateResponse(request, "login.html", {
        "error": None,
        "recuperado": recuperado == "1"
    })
 
 
@router.post("/login")
def login_post(
    request: Request,
    cedula: str = Form(...),
    session: Session = Depends(get_session)
):
    cedula = cedula.strip()
    if not cedula:
        return templates.TemplateResponse(request, "login.html", {"error": "Debes ingresar tu cédula.", "recuperado": False})
    if not cedula.isdigit():
        return templates.TemplateResponse(request, "login.html", {"error": "La cédula solo debe contener números.", "recuperado": False})
 
    usuario = session.get(Usuario, cedula)
    if not usuario:
        return templates.TemplateResponse(request, "login.html", {"error": "No se encontró ninguna cuenta con esa cédula.", "recuperado": False})
 
    mascotas_usuario = session.exec(select(Mascota).where(Mascota.cedula_dueno == cedula)).all()
    if mascotas_usuario:
        mascota_activa = mascotas_usuario[0]
        return templates.TemplateResponse(request, "dashboard.html", {
            "nombre": usuario.nombre_completo,
            "cedula": cedula,
            "mascotas": mascotas_usuario,
            "mascota_activa": mascota_activa,
            "vacunas": session.exec(select(Vacuna).where(Vacuna.id_mascota == mascota_activa.id_mascota)).all(),
            "historial": session.exec(select(Historial).where(Historial.id_mascota == mascota_activa.id_mascota)).all(),
            "bitacora": session.exec(select(Bitacora).where(Bitacora.id_mascota == mascota_activa.id_mascota)).all()
        })
    else:
        return templates.TemplateResponse(request, "registrar_mascota.html", {
            "cedula_dueno": cedula, "errores": {}, "form": {}
        })
 
 
@router.get("/recuperar-contrasena")
def recuperar_contrasena_page(request: Request):
    return templates.TemplateResponse(request, "recuperar_contrasena.html", {"error": None})
 
 
@router.post("/recuperar-contrasena")
def recuperar_contrasena_post(
    request: Request,
    cedula: str = Form(...),
    correo: str = Form(...),
    nueva_password: str = Form(...),
    nueva_password_confirm: str = Form(...),
    session: Session = Depends(get_session)
):
    cedula = cedula.strip()
    correo = correo.strip()
    error = None
 
    if not cedula.isdigit():
        error = "La cédula solo debe contener números."
    elif len(nueva_password) < 6:
        error = "La nueva contraseña debe tener al menos 6 caracteres."
    elif nueva_password != nueva_password_confirm:
        error = "Las contraseñas no coinciden."
    else:
        usuario = session.get(Usuario, cedula)
        if not usuario or usuario.correo.lower() != correo.lower():
            error = "No encontramos una cuenta con esa cédula y correo. Verifica los datos."
        else:
            usuario.password = nueva_password
            session.add(usuario)
            session.commit()
            return RedirectResponse("/login?recuperado=1", status_code=303)
 
    return templates.TemplateResponse(request, "recuperar_contrasena.html", {
        "error": error
    })