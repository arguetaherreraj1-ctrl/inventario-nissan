import os
import shutil
import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database

app = FastAPI(title="Inventario Nissan - Almacén Inteligente 3D")

# Asegurar directorios
os.makedirs("fotos", exist_ok=True)
app.mount("/fotos", StaticFiles(directory="fotos"), name="fotos")

# Función para conectarse a la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ESQUEMAS DE DATOS ---
class TecnicoCreate(BaseModel):
    nombre: str
    nip: str

class TecnicoLogin(BaseModel):
    nip: str

class PrestamoRequest(BaseModel):
    herramienta_clave: str
    tecnico_nombre: str

class DevolverRequest(BaseModel):
    herramienta_clave: str

# --- INICIALIZACIÓN DE DATOS SEMILLA (Para pruebas inmediatas) ---
@app.on_event("startup")
def startup_db():
    db = database.SessionLocal()
    try:
        # Crear técnico por defecto si no existe
        if not db.query(database.Tecnico).first():
            db.add(database.Tecnico(nombre="Jorge Argueta", nip="1234"))
            db.add(database.Tecnico(nombre="Carlos Mendoza", nip="5678"))
            db.commit()

        # Crear herramientas de demostración para los estantes A, B y C
        if not db.query(database.Herramienta).first():
            demo_herramientas = [
                database.Herramienta(clave="NI-101", descripcion="PISTOLA DE IMPACTO NEUMÁTICA 1/2", ubicacion="A1", cantidad_total=4, cantidad_disponible=3, foto_url=""),
                database.Herramienta(clave="NI-102", descripcion="TORQUÍMETRO DIGITAL 3/8", ubicacion="A2", cantidad_total=2, cantidad_disponible=2, foto_url=""),
                database.Herramienta(clave="NI-201", descripcion="ESCÁNER NISSAN CONSULT III PLUS", ubicacion="B1", cantidad_total=3, cantidad_disponible=1, foto_url=""),
                database.Herramienta(clave="NI-202", descripcion="MULTÍMETRO AUTOMOTRIZ FLUKE", ubicacion="B2", cantidad_total=5, cantidad_disponible=5, foto_url=""),
                database.Herramienta(clave="NI-301", descripcion="EXTRACTOR DE BALEROS Y POLEAS", ubicacion="C1", cantidad_total=2, cantidad_disponible=2, foto_url=""),
                database.Herramienta(clave="NI-302", descripcion="KIT CALIBRADOR DE FRENOS DE DISCO", ubicacion="C2", cantidad_total=3, cantidad_disponible=2, foto_url=""),
            ]
            db.add_all(demo_herramientas)
            db.commit()
    finally:
        db.close()

# --- RUTAS DE LA API ---

@app.get("/")
def inicio():
    return FileResponse("index.html")

@app.post("/registrar_tecnico")
def registrar_tecnico(datos: TecnicoCreate, db: Session = Depends(get_db)):
    existe = db.query(database.Tecnico).filter(database.Tecnico.nip == datos.nip).first()
    if existe:
        return {"error": "Este NIP ya está registrado."}
    nuevo = database.Tecnico(nombre=datos.nombre.strip(), nip=datos.nip.strip())
    db.add(nuevo)
    db.commit()
    return {"mensaje": "Registro exitoso", "nombre": nuevo.nombre}

@app.post("/login_tecnico")
def login_tecnico(datos: TecnicoLogin, db: Session = Depends(get_db)):
    tecnico = db.query(database.Tecnico).filter(database.Tecnico.nip == datos.nip.strip()).first()
    if not tecnico:
        return {"error": "NIP incorrecto o no registrado."}
    return {"mensaje": "Login exitoso", "nombre": tecnico.nombre, "id": tecnico.id}

@app.get("/herramientas")
def listar_herramientas(db: Session = Depends(get_db)):
    return db.query(database.Herramienta).all()

@app.post("/agregar_herramienta")
def agregar_herramienta(
    clave: str = Form(...),
    descripcion: str = Form(...),
    ubicacion: str = Form(...),
    cantidad: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    clave = clave.strip().upper()
    existe = db.query(database.Herramienta).filter(database.Herramienta.clave == clave).first()
    if existe:
        return {"error": "Ya existe una herramienta con esa clave."}

    foto_url = ""
    if foto and foto.filename:
        nombre_limpio = foto.filename.replace(" ", "_")
        ruta = f"fotos/{clave}_{nombre_limpio}"
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/{ruta}"

    nueva = database.Herramienta(
        clave=clave, 
        descripcion=descripcion.strip().upper(), 
        ubicacion=ubicacion.strip().upper(),
        cantidad_total=cantidad, 
        cantidad_disponible=cantidad, 
        foto_url=foto_url
    )
    db.add(nueva)
    db.commit()
    return {"mensaje": "Herramienta guardada correctamente"}

@app.post("/prestar")
def prestar_herramienta(datos: PrestamoRequest, db: Session = Depends(get_db)):
    herr = db.query(database.Herramienta).filter(database.Herramienta.clave == datos.herramienta_clave).first()
    if not herr or herr.cantidad_disponible <= 0:
        return {"error": "Herramienta no disponible o en uso."}
    
    herr.cantidad_disponible -= 1
    nuevo_prestamo = database.Prestamo(
        herramienta_clave=datos.herramienta_clave,
        tecnico_nombre=datos.tecnico_nombre,
        fecha_salida=datetime.datetime.utcnow()
    )
    db.add(nuevo_prestamo)
    db.commit()
    return {"mensaje": "Préstamo registrado", "ubicacion": herr.ubicacion}

@app.post("/devolver")
def devolver_herramienta(datos: DevolverRequest, db: Session = Depends(get_db)):
    herr = db.query(database.Herramienta).filter(database.Herramienta.clave == datos.herramienta_clave).first()
    if not herr or herr.cantidad_disponible >= herr.cantidad_total:
        return {"error": "Esta herramienta ya está registrada como devuelta o no existe."}
    
    herr.cantidad_disponible += 1
    
    prestamo_activo = db.query(database.Prestamo).filter(
        database.Prestamo.herramienta_clave == datos.herramienta_clave,
        database.Prestamo.fecha_devolucion == None
    ).order_by(database.Prestamo.id.desc()).first()
    
    if prestamo_activo:
        prestamo_activo.fecha_devolucion = datetime.datetime.utcnow()
        
    db.commit()
    return {"mensaje": "Pieza devuelta al estante correctamente."}

@app.get("/historial")
def ver_historial(db: Session = Depends(get_db)):
    return db.query(database.Prestamo).order_by(database.Prestamo.id.desc()).all()

@app.get("/estadisticas")
def estadisticas(db: Session = Depends(get_db)):
    total_piezas = db.query(database.Herramienta).count()
    en_prestamo = db.query(database.Prestamo).filter(database.Prestamo.fecha_devolucion == None).count()
    total_tecnicos = db.query(database.Tecnico).count()
    return {
        "total_piezas": total_piezas,
        "en_prestamo": en_prestamo,
        "total_tecnicos": total_tecnicos
    }
