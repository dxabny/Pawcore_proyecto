# PawCore - Sistema de Gestión Veterinaria

Proyecto Integrador — Desarrollo de Software
Universidad Católica de Colombia · Ingeniería de Sistemas y Computación


## Descripción del Proyecto

PawCore es una aplicación web desarrollada con Python y FastAPI para gestionar la información clínica de una veterinaria. El sistema permite a los dueños consultar el estado de salud de sus mascotas y al veterinario administrar historiales, vacunas y consultas desde un panel centralizado con visualizaciones estadísticas.


## Criterio 13 - Datos Coherentes en el Sistema

Todos los datos ingresados al sistema son coherentes, realistas y representativos de un entorno veterinario real. Los formularios de registro validan que la informacion sea correcta y consistente (cedulas numericas, correos validos, telefonos de diez digitos, pesos y edades razonables para cada especie).

### Credenciales de acceso

Panel veterinario:

| Usuario | Contrasena |
|---|---|
| admin | veterinario3 |


## Criterio 15 - Reportes / Dashboards / Graficas en HTML

El panel del veterinario (`/admin/dashboard`) incluye visualizaciones estadísticas desarrolladas completamente en HTML y CSS, sin dependencias externas. Las graficas se alimentan con datos reales calculados en el backend de FastAPI y renderizados en la plantilla con Jinja2.

### Grafica 1 - Mascotas por especie (barras horizontales CSS)
Muestra cuantas mascotas hay registradas de cada especie: perros, gatos, conejos y aves. El ancho de cada barra es proporcional al total, calculado en el servidor. Permite al veterinario identificar que tipo de pacientes son mas frecuentes en la clinica.

### Grafica 2 - Distribucion por genero (barras CSS)
Muestra la cantidad de mascotas macho vs hembra registradas en el sistema. Util para entender la distribucion demografica de los pacientes.

### Grafica 3 - Consultas por tipo de evento (barras horizontales CSS)
Agrupa todas las entradas de la bitacora por tipo: Consulta, Control, Urgencia, Cirugia y Vacunacion. Permite ver que tipo de atencion es mas demandada en la clinica.

Todas las visualizaciones se renderizan directamente en HTML con estilos CSS inline generados por Jinja2. Los datos son calculados en tiempo real desde la base de datos cada vez que se accede al panel.


## Criterio 16 - Repositorio GitHub Completo y Organizado

### Estructura del proyecto

```
PawCore/
├── main.py                       # Punto de entrada, registro de routers
├── database.py                   # Configuracion de la base de datos SQLite
├── entidades.py                  # Modelos SQLModel (tablas de la BD)
├── utils.py                      # Funciones compartidas (parsear_fecha, EVENTOS_VALIDOS)
├── requirements.txt              # Dependencias del proyecto
├── .gitignore                    # Excluye __pycache__, .db, venv/
├── README.md
│
├── routers/
│   ├── __init__.py
│   ├── usuarios.py               # Registro, login, recuperar contrasena
│   ├── mascotas.py               # Registro y dashboard de mascotas
│   ├── admin_auth.py             # Login del veterinario
│   ├── admin_dashboard.py        # Panel admin con graficas estadisticas
│   ├── vacunas.py                # Agregar, editar y eliminar vacunas
│   ├── historial.py              # Agregar y editar historial clinico
│   └── bitacora.py               # Agregar y editar bitacora de consultas
│
├── static/
│   ├── styles.css
│   └── img/
│
└── templates/
    ├── pawcore_landing.html
    ├── login.html
    ├── registro.html
    ├── recuperar_contrasena.html
    ├── registrar_mascota.html
    ├── dashboard.html
    ├── admin_login.html
    ├── admin_dashboard.html
    ├── editar_historial.html
    ├── actualizar_vacuna.html
    └── actualizar_bitacora.html
```

### Archivo .gitignore

El repositorio incluye un `.gitignore` configurado para excluir:

```
__pycache__/
*.pyc
*.db
venv/
.env
.DS_Store
```

### Instalacion y ejecucion

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/pawcore.git
cd pawcore
```

2. Crear entorno virtual e instalar dependencias:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

 Ejecutar la aplicacion:

```bash
uvicorn main:app --reload
```


### Dependencias (requirements.txt)

```
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlmodel==0.0.22
sqlalchemy==2.0.40
jinja2==3.1.6
python-multipart==0.0.20
```

---

## Tecnologias Utilizadas

| Capa | Tecnologia |
|---|---|
| Backend | Python 3.12 + FastAPI |
| ORM | SQLModel + SQLAlchemy |
| Base de datos | SQLite |
| Frontend | HTML5 + CSS3 + Jinja2 |
| Servidor | Uvicorn |

---

## Autora

Daniela — Proyecto academico
Asignatura: Desarrollo de Software
Universidad Católica de Colombia
