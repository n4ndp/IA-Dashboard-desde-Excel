"""Project management routes.

GET    /api/users/{user_id}/projects                        — list user's projects
POST   /api/users/{user_id}/projects                        — create project with upload
GET    /api/users/{user_id}/projects/{project_id}           — get project detail
PATCH  /api/users/{user_id}/projects/{project_id}           — rename project
DELETE /api/users/{user_id}/projects/{project_id}           — delete project cascade
POST   /api/users/{user_id}/projects/{project_id}/upload    — add sheets to project
"""
import os

from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    ProjectListResponse,
    ProjectSummary,
    ProjectDetail as ProjectDetailSchema,
    ProjectRenameRequest,
    ProjectUploadResponse,
    TableSummary,
    ColumnSummary,
    TableSummaryOut,
)
from services.user_service import get_user
from services.excel_service import (
    create_project,
    add_sheets_to_project,
    list_user_projects,
    get_project_detail,
    rename_project,
    delete_project,
)

router = APIRouter()

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))


def _validate_user(db: Session, user_id: int) -> dict:
    """Validate that a user exists, raising 404 if not."""
    try:
        return get_user(db, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


def _validate_ownership(db: Session, user_id: int, project_id: int) -> dict:
    """Validate user exists AND project belongs to that user.

    Returns the project detail dict on success.
    """
    _validate_user(db, user_id)

    try:
        detail = get_project_detail(db, project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify the project belongs to the specified user via the proyecto query
    from models import Proyecto
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None or proyecto.usuario_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")

    return detail


@router.get("/users/{user_id}/projects", response_model=ProjectListResponse)
def list_projects(user_id: int, db: Session = Depends(get_db)):
    """List all projects for a user with table counts."""
    try:
        projects = list_user_projects(db, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ProjectListResponse(
        projects=[ProjectSummary(**p) for p in projects]
    )


@router.post("/users/{user_id}/projects", response_model=ProjectUploadResponse)
async def create_new_project(
    user_id: int,
    file: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Create a new project for a user with an Excel file upload."""
    _validate_user(db, user_id)

    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .xlsx files are accepted.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds size limit.")

    display_name = project_name.strip() if project_name and project_name.strip() else file.filename

    try:
        result = create_project(
            db=db,
            user_id=user_id,
            filename=display_name,
            file_bytes=file_bytes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ProjectUploadResponse(
        user_id=result["user_id"],
        project_id=result["project_id"],
        tables=[
            TableSummary(
                table_id=t["table_id"],
                sheet_name=t["sheet_name"],
                columns=[ColumnSummary(**c) for c in t["columns"]],
                row_count=t["row_count"],
            )
            for t in result["tables"]
        ],
    )


@router.get("/users/{user_id}/projects/{project_id}", response_model=ProjectDetailSchema)
def get_project(user_id: int, project_id: int, db: Session = Depends(get_db)):
    """Get full project detail with lightweight table summaries."""
    detail = _validate_ownership(db, user_id, project_id)

    return ProjectDetailSchema(
        id=detail["id"],
        nombre_archivo=detail["nombre_archivo"],
        fecha_creacion=detail["fecha_creacion"],
        tables=[TableSummaryOut(**t) for t in detail["tables"]],
    )


@router.patch("/users/{user_id}/projects/{project_id}", response_model=ProjectDetailSchema)
def rename_project_endpoint(
    user_id: int,
    project_id: int,
    body: ProjectRenameRequest,
    db: Session = Depends(get_db),
):
    """Rename a project."""
    _validate_ownership(db, user_id, project_id)

    try:
        detail = rename_project(db, project_id, body.nombre_archivo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ProjectDetailSchema(
        id=detail["id"],
        nombre_archivo=detail["nombre_archivo"],
        fecha_creacion=detail["fecha_creacion"],
        tables=[TableSummaryOut(**t) for t in detail["tables"]],
    )


@router.delete("/users/{user_id}/projects/{project_id}", status_code=204)
def remove_project(user_id: int, project_id: int, db: Session = Depends(get_db)):
    """Delete a project and cascade all related data."""
    _validate_ownership(db, user_id, project_id)

    try:
        delete_project(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/users/{user_id}/projects/{project_id}/upload", response_model=ProjectUploadResponse)
async def upload_to_existing_project(
    user_id: int,
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload additional Excel sheets into an existing project."""
    _validate_ownership(db, user_id, project_id)

    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .xlsx files are accepted.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds size limit.")

    try:
        result = add_sheets_to_project(
            db=db,
            project_id=project_id,
            file_bytes=file_bytes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ProjectUploadResponse(
        user_id=user_id,
        project_id=result["project_id"],
        tables=[
            TableSummary(
                table_id=t["table_id"],
                sheet_name=t["sheet_name"],
                columns=[ColumnSummary(**c) for c in t["columns"]],
                row_count=t["row_count"],
            )
            for t in result["tables"]
        ],
    )