"""ORM models for the Excel AI Dashboard.

Defines 5 entities with their relationships:
    Usuario → Proyecto → Tabla → Columna
                            └→ Fila
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from database import Base


class Usuario(Base):
    """A user identified by name. Created on first upload, reused thereafter."""

    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)

    proyectos = relationship("Proyecto", back_populates="usuario")


class Proyecto(Base):
    """An upload session. Each file upload creates a new Proyecto for the user."""

    __tablename__ = "proyecto"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    nombre_archivo = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="proyectos")
    tablas = relationship("Tabla", back_populates="proyecto", cascade="all, delete-orphan")


class Tabla(Base):
    """Represents a single sheet from the uploaded Excel file."""

    __tablename__ = "tabla"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"), nullable=False)
    nombre_hoja = Column(String, nullable=False)

    proyecto = relationship("Proyecto", back_populates="tablas")
    columnas = relationship("Columna", back_populates="tabla", cascade="all, delete-orphan")
    filas = relationship("Fila", back_populates="tabla", cascade="all, delete-orphan")


class Columna(Base):
    """A column within a table, with its inferred data type."""

    __tablename__ = "columna"

    id = Column(Integer, primary_key=True, index=True)
    tabla_id = Column(Integer, ForeignKey("tabla.id"), nullable=False)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # "string" | "number" | "date"

    tabla = relationship("Tabla", back_populates="columnas")


class Fila(Base):
    """A row of data stored as JSONB, keyed by column name."""

    __tablename__ = "fila"

    id = Column(Integer, primary_key=True, index=True)
    tabla_id = Column(Integer, ForeignKey("tabla.id"), nullable=False)
    orden = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)

    tabla = relationship("Tabla", back_populates="filas")
