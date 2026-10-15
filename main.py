import os
import shutil
import datetime
import socket
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

# --- INICIALIZACIÓN DE DATOS SEMILLA (57 Piezas Físicas Oficiales) ---
@app.on_event("startup")
def startup_db():
    db = database.SessionLocal()
    try:
        # Crear técnicos por defecto si no existen
        if not db.query(database.Tecnico).first():
            db.add(database.Tecnico(nombre="Jorge Argueta", nip="1234"))
            db.add(database.Tecnico(nombre="Carlos Mendoza", nip="5678"))
            db.commit()

        # Cargar catálogo de 57 piezas físicas si no están en la base de datos
        try:
            from cargar_datos import datos_herramientas
            for item in datos_herramientas:
                existe = db.query(database.Herramienta).filter(database.Herramienta.clave == item["clave"]).first()
                if not existe:
                    db.add(database.Herramienta(
                        clave=item["clave"],
                        descripcion=item["descripcion"],
                        ubicacion=item["ubicacion"],
                        cantidad_total=item["cantidad"],
                        cantidad_disponible=item["cantidad"],
                        foto_url=""
                    ))
            db.commit()
            print("[OK] Base de datos sincronizada con las piezas oficiales Nissan.")
        except Exception as e:
            print("Aviso al verificar catálogo de herramientas:", e)
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

@app.get("/cargar_catalogo_completo")
@app.post("/cargar_catalogo_completo")
def cargar_catalogo_completo(db: Session = Depends(get_db)):
    """Sincroniza y asegura las 57 piezas físicas de inventario Nissan en la base de datos."""
    from cargar_datos import datos_herramientas
    agregadas = 0
    actualizadas = 0
    for item in datos_herramientas:
        existe = db.query(database.Herramienta).filter(database.Herramienta.clave == item["clave"]).first()
        if not existe:
            nueva = database.Herramienta(
                clave=item["clave"],
                descripcion=item["descripcion"],
                ubicacion=item["ubicacion"],
                cantidad_total=item["cantidad"],
                cantidad_disponible=item["cantidad"],
                foto_url=""
            )
            db.add(nueva)
            agregadas += 1
        else:
            existe.descripcion = item["descripcion"]
            existe.ubicacion = item["ubicacion"]
            existe.cantidad_total = item["cantidad"]
            actualizadas += 1
    db.commit()
    return {
        "mensaje": f"Catálogo sincronizado exitosamente: {agregadas} piezas agregadas, {actualizadas} actualizadas.",
        "total": agregadas + actualizadas
    }

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
        nombre_archivo = f"{clave}_{foto.filename}"
        ruta_guardado = os.path.join("fotos", nombre_archivo)
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/fotos/{nombre_archivo}"

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
    return {"mensaje": "Herramienta agregada exitosamente", "clave": nueva.clave}

@app.post("/prestar")
def prestar_herramienta(datos: PrestamoRequest, db: Session = Depends(get_db)):
    herr = db.query(database.Herramienta).filter(database.Herramienta.clave == datos.herramienta_clave).first()
    if not herr:
        return {"error": "Herramienta no encontrada."}
    if herr.cantidad_disponible <= 0:
        return {"error": "No hay unidades disponibles de esta herramienta."}

    herr.cantidad_disponible -= 1
    nuevo_prestamo = database.Prestamo(
        herramienta_clave=datos.herramienta_clave,
        tecnico_nombre=datos.tecnico_nombre
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

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@app.get("/info_red")
def info_red():
    ip = obtener_ip_local()
    return {
        "ip": ip,
        "puerto": 8000,
        "url_movil": f"http://{ip}:8000"
    }
