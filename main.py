import os
import shutil
import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database

# 1. Inicializar app y crear carpeta para fotos si no existe
app = FastAPI(title="Inventario Nissan")
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

# --- RUTAS DE LA API ---

# 1. Ruta principal: Entrega la página web (index.html)
@app.get("/")
def inicio():
    return FileResponse("index.html")

# 2. Registrar un nuevo técnico
@app.post("/registrar_tecnico")
def registrar_tecnico(datos: TecnicoCreate, db: Session = Depends(get_db)):
    existe = db.query(database.Tecnico).filter(database.Tecnico.nip == datos.nip).first()
    if existe:
        return {"error": "Este NIP ya está registrado."}
    nuevo = database.Tecnico(nombre=datos.nombre, nip=datos.nip)
    db.add(nuevo)
    db.commit()
    return {"mensaje": "Registro exitoso", "nombre": datos.nombre}

# 3. Iniciar sesión con NIP
@app.post("/login_tecnico")
def login_tecnico(datos: TecnicoLogin, db: Session = Depends(get_db)):
    tecnico = db.query(database.Tecnico).filter(database.Tecnico.nip == datos.nip).first()
    if not tecnico:
        return {"error": "NIP incorrecto o no registrado."}
    return {"mensaje": "Login exitoso", "nombre": tecnico.nombre}

# 4. Listar todas las herramientas del catálogo
@app.get("/herramientas")
def listar_herramientas(db: Session = Depends(get_db)):
    return db.query(database.Herramienta).all()

# 5. Agregar una pieza nueva (¡Con soporte para FOTO!)
@app.post("/agregar_herramienta")
def agregar_herramienta(
    clave: str = Form(...),
    descripcion: str = Form(...),
    ubicacion: str = Form(...),
    cantidad: int = Form(...),
    foto: UploadFile = File(None), # Recibe el archivo de imagen
    db: Session = Depends(get_db)
):
    existe = db.query(database.Herramienta).filter(database.Herramienta.clave == clave).first()
    if existe:
        return {"error": "Ya existe una herramienta con esa clave."}

    foto_url = ""
    # Si el usuario subió foto, la guardamos
    if foto and foto.filename:
        ruta = f"fotos/{clave}_{foto.filename}"
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/{ruta}"

    nueva = database.Herramienta(
        clave=clave, 
        descripcion=descripcion, 
        ubicacion=ubicacion,
        cantidad_total=cantidad, 
        cantidad_disponible=cantidad, 
        foto_url=foto_url
    )
    db.add(nueva)
    db.commit()
    return {"mensaje": "Herramienta guardada correctamente"}

# 6. Prestar una herramienta (Check-out)
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

# 7. Ver el historial de préstamos
@app.get("/historial")
def ver_historial(db: Session = Depends(get_db)):
    # Devuelve la lista ordenada desde el más reciente
    return db.query(database.Prestamo).order_by(database.Prestamo.id.desc()).all()

    # 8. Esquema para recibir devoluciones
class DevolverRequest(BaseModel):
    herramienta_clave: str

# 9. Ruta para devolver una herramienta (Check-in)
@app.post("/devolver")
def devolver_herramienta(datos: DevolverRequest, db: Session = Depends(get_db)):
    herr = db.query(database.Herramienta).filter(database.Herramienta.clave == datos.herramienta_clave).first()
    
    if not herr or herr.cantidad_disponible >= herr.cantidad_total:
        return {"error": "Esta herramienta ya está registrada como devuelta."}
    
    # Sumar la pieza de vuelta al inventario
    herr.cantidad_disponible += 1
    
    # Buscar en la bitácora quién la tenía y ponerle fecha de devolución
    prestamo_activo = db.query(database.Prestamo).filter(
        database.Prestamo.herramienta_clave == datos.herramienta_clave,
        database.Prestamo.fecha_devolucion == None
    ).order_by(database.Prestamo.id.desc()).first()
    
    if prestamo_activo:
        prestamo_activo.fecha_devolucion = datetime.datetime.utcnow()
        
    db.commit()
    return {"mensaje": "Pieza devuelta al estante correctamente."}