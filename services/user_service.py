"""User management service.

Handles get-or-create logic and user lookups.
"""

from sqlalchemy.orm import Session

from models import Usuario


def get_or_create_user(db: Session, nombre: str) -> dict:
    """Get an existing user by name, or create a new one.

    Args:
        db: SQLAlchemy session.
        nombre: The user's display name (already stripped by schema).

    Returns:
        A dict with id and nombre matching UserResponse.

    Raises:
        ValueError: If nombre is empty after stripping.
    """
    if not nombre or not nombre.strip():
        raise ValueError("Name cannot be empty")

    nombre = nombre.strip()

    usuario = db.query(Usuario).filter(Usuario.nombre == nombre).first()
    if usuario is None:
        usuario = Usuario(nombre=nombre)
        db.add(usuario)
        db.flush()

    return {"id": usuario.id, "nombre": usuario.nombre}


def get_user(db: Session, user_id: int) -> dict:
    """Look up a user by ID.

    Args:
        db: SQLAlchemy session.
        user_id: The user's database ID.

    Returns:
        A dict with id and nombre matching UserResponse.

    Raises:
        ValueError: If the user does not exist.
    """
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise ValueError("User not found")

    return {"id": usuario.id, "nombre": usuario.nombre}
