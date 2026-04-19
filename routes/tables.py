"""Table management routes.

GET    /api/users/{user_id}/projects/{project_id}/tables                     — list table metadata
GET    /api/users/{user_id}/projects/{project_id}/tables/{table_id}          — get single table full data
DELETE /api/users/{user_id}/projects/{project_id}/tables/{table_id}          — delete single table
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    TableListResponse,
    TableSummaryOut,
    SingleTableResponse,
    ColumnOut,
    RowOut,
)
from services.user_service import get_user
from services.excel_service import (
    get_project_detail,
    get_single_table,
    delete_table,
)
from models import Proyecto, Tabla

router = APIRouter()


def _validate_user(db: Session, user_id: int) -> dict:
    """Validate that a user exists, raising 404 if not."""
    try:
        return get_user(db, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


def _validate_project_ownership(db: Session, user_id: int, project_id: int) -> None:
    """Validate user exists AND project belongs to that user."""
    _validate_user(db, user_id)

    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None or proyecto.usuario_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")


def _validate_table_ownership(db: Session, project_id: int, table_id: int) -> None:
    """Validate that a table belongs to the specified project."""
    tabla = db.query(Tabla).filter(Tabla.id == table_id).first()
    if tabla is None or tabla.proyecto_id != project_id:
        raise HTTPException(status_code=404, detail="Table not found")


@router.get(
    "/users/{user_id}/projects/{project_id}/tables",
    response_model=TableListResponse,
)
def list_tables(user_id: int, project_id: int, db: Session = Depends(get_db)):
    """List table metadata for a project (no row data)."""
    _validate_project_ownership(db, user_id, project_id)

    try:
        detail = get_project_detail(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return TableListResponse(
        tables=[TableSummaryOut(**t) for t in detail["tables"]]
    )


@router.get(
    "/users/{user_id}/projects/{project_id}/tables/{table_id}",
    response_model=SingleTableResponse,
)
def get_table(
    user_id: int,
    project_id: int,
    table_id: int,
    db: Session = Depends(get_db),
):
    """Get full data for a single table (columns + rows)."""
    _validate_project_ownership(db, user_id, project_id)
    _validate_table_ownership(db, project_id, table_id)

    try:
        result = get_single_table(db, table_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return SingleTableResponse(
        id=result["id"],
        sheet_name=result["sheet_name"],
        columns=[ColumnOut(**c) for c in result["columns"]],
        rows=[RowOut(**r) for r in result["rows"]],
    )


@router.delete(
    "/users/{user_id}/projects/{project_id}/tables/{table_id}",
    status_code=204,
)
def remove_table(
    user_id: int,
    project_id: int,
    table_id: int,
    db: Session = Depends(get_db),
):
    """Delete a single table (cascades columns and rows)."""
    _validate_project_ownership(db, user_id, project_id)
    _validate_table_ownership(db, project_id, table_id)

    try:
        delete_table(db, table_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
