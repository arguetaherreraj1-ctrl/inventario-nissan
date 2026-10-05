import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

# 1. Leer la URL de la base de datos desde la Nube (si no existe, usa SQLite local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventario.db")

# 2. Corregir el formato de URL que entrega Render para PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Crear la conexión dependiendo del tipo de base de datos
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL) # PostgreSQL no necesita check_same_thread

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ... (De aquí hacia abajo deja tus clases Tecnico, Herramienta y Prestamo igualitas) ...
# NUEVA TABLA: Técnicos (Para el Login y NIP)
class Tecnico(Base):
    __tablename__ = "tecnicos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    nip = Column(String, unique=True, index=True)

# Tabla de Herramientas
class Herramienta(Base):
    __tablename__ = "herramientas"
    clave = Column(String, primary_key=True, index=True)
    descripcion = Column(String, index=True)
    ubicacion = Column(String)
    cantidad_total = Column(Integer)
    cantidad_disponible = Column(Integer)
    foto_url = Column(String, nullable=True) # Aquí guardaremos la ruta de la foto

    prestamos = relationship("Prestamo", back_populates="herramienta")

# Tabla de la Bitácora de Préstamos
class Prestamo(Base):
    __tablename__ = "prestamos"
    id = Column(Integer, primary_key=True, index=True)
    herramienta_clave = Column(String, ForeignKey("herramientas.clave"))
    tecnico_nombre = Column(String, index=True)
    fecha_salida = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_devolucion = Column(DateTime, nullable=True)

    herramienta = relationship("Herramienta", back_populates="prestamos")

# Aplicar cambios
Base.metadata.create_all(bind=engine)