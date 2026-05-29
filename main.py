from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session, select
from database import engine
from entidades import Admin
from routers import usuarios, mascotas, admin_auth, admin_dashboard, vacunas, historial, bitacora

app = FastAPI(title="PawCore API", description="¡Bienvenido a PawCore!", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(usuarios.router)
app.include_router(mascotas.router)
app.include_router(admin_auth.router)
app.include_router(admin_dashboard.router)
app.include_router(vacunas.router)
app.include_router(historial.router)
app.include_router(bitacora.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin_existente = session.exec(select(Admin).where(Admin.usuario == "admin")).first()
        if not admin_existente:
            admin = Admin(usuario="admin", contrasena="veterinario3")
            session.add(admin)
            session.commit()
