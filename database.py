import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventario.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Tecnico(Base):
    __tablename__ = "tecnicos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    nip = Column(String, unique=True, index=True)

class Herramienta(Base):
    __tablename__ = "herramientas"
    clave = Column(String, primary_key=True, index=True)
    descripcion = Column(String, index=True)
    ubicacion = Column(String)
    cantidad_total = Column(Integer)
    cantidad_disponible = Column(Integer)
    foto_url = Column(String, nullable=True)

    prestamos = relationship("Prestamo", back_populates="herramienta")

class Prestamo(Base):
    __tablename__ = "prestamos"
    id = Column(Integer, primary_key=True, index=True)
    herramienta_clave = Column(String, ForeignKey("herramientas.clave"))
    tecnico_nombre = Column(String, index=True)
    fecha_salida = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_devolucion = Column(DateTime, nullable=True)

    herramienta = relationship("Herramienta", back_populates="prestamos")

Base.metadata.create_all(bind=engine)
