from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import date


class Usuario(SQLModel, table=True):
    cedula: str = Field(primary_key=True)
    nombre_completo: str
    correo: str
    telefono: str
    direccion: str
    password: Optional[str] = Field(default=None)

    mascotas: List["Mascota"] = Relationship(back_populates="dueno")


class Mascota(SQLModel, table=True):
    id_mascota: int = Field(primary_key=True)
    nombre_mascota: str
    especie: str
    raza: str
    edad: int
    peso: float
    genero: str
    color: str
    estado_reproductivo: str

    cedula_dueno: Optional[str] = Field(default=None, foreign_key="usuario.cedula")
    dueno: Optional[Usuario] = Relationship(back_populates="mascotas")

    vacunas: List["Vacuna"] = Relationship(back_populates="mascota")
    bitacoras: List["Bitacora"] = Relationship(back_populates="mascota")
    historiales: List["Historial"] = Relationship(back_populates="mascota")


class Vacuna(SQLModel, table=True):
    id_vacuna: Optional[int] = Field(default=None, primary_key=True)
    nombre_vacuna: str
    fecha_aplicacion: date
    proxima_dosis: date

    id_mascota: Optional[int] = Field(default=None, foreign_key="mascota.id_mascota")
    mascota: Optional[Mascota] = Relationship(back_populates="vacunas")


class Bitacora(SQLModel, table=True):
    id_bitacora: Optional[int] = Field(default=None, primary_key=True)
    fecha: date
    tipo_evento: str
    motivo: str
    sintomas: str
    diagnostico: str
    procedimiento: str
    medicacion: Optional[str] = "Ninguna"
    observaciones: str

    id_mascota: Optional[int] = Field(default=None, foreign_key="mascota.id_mascota")
    mascota: Optional[Mascota] = Relationship(back_populates="bitacoras")


class Historial(SQLModel, table=True):
    id_historial: Optional[int] = Field(default=None, primary_key=True)
    fecha: date
    enfermedades_previas: Optional[str] = "Ninguna"
    cirugias_previas: Optional[str] = "Ninguna"
    alergias: Optional[str] = "Ninguna"
    tratamientos_previos: Optional[str] = "Ninguno"

    id_mascota: Optional[int] = Field(default=None, foreign_key="mascota.id_mascota")
    mascota: Optional[Mascota] = Relationship(back_populates="historiales")


class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario: str
    contrasena: str