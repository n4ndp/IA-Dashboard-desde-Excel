"""Pydantic schemas for request/response serialization."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


# --- User schemas (NEW) ---

class UserCreate(BaseModel):
    """Request body for POST /api/users."""
    nombre: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)


class UserResponse(BaseModel):
    """Response for user endpoints."""
    id: int
    nombre: str


# --- Project rename (NEW) ---

class ProjectRenameRequest(BaseModel):
    """Request body for PATCH project rename."""
    nombre_archivo: str = Field(..., min_length=1, max_length=200)


# --- Upload response ---

class ColumnSummary(BaseModel):
    """Column name and inferred type returned after upload."""
    name: str
    type: str


class TableSummary(BaseModel):
    """Summary of a parsed table returned after upload."""
    table_id: int
    sheet_name: str
    columns: list[ColumnSummary]
    row_count: int


class ProjectUploadResponse(BaseModel):
    """Response for POST /api/users/{user_id}/projects and upload endpoints."""
    user_id: int
    project_id: int
    tables: list[TableSummary]


# --- Table schemas ---

class ColumnOut(BaseModel):
    """A column with its id, name and type."""
    id: int
    name: str
    type: str


class RowOut(BaseModel):
    """A row with its id and JSONB data."""
    id: int
    data: dict[str, Any]


class SingleTableResponse(BaseModel):
    """Full table detail: columns + rows for a single table."""
    id: int
    sheet_name: str
    columns: list[ColumnOut]
    rows: list[RowOut]


class TableListResponse(BaseModel):
    """Response for GET table metadata list (no row data)."""
    tables: list['TableSummaryOut']


# --- Project listing & detail ---

class TableSummaryOut(BaseModel):
    """Lightweight table summary for project detail view."""
    id: int
    nombre_hoja: str
    row_count: int
    column_count: int


class ProjectSummary(BaseModel):
    """Project card data for the listing view."""
    id: int
    nombre_archivo: str
    fecha_creacion: datetime
    tabla_count: int


class ProjectListResponse(BaseModel):
    """Response for GET /api/users/{user_id}/projects."""
    projects: list[ProjectSummary]


class ProjectDetail(BaseModel):
    """Full project detail with tables for the project detail view."""
    id: int
    nombre_archivo: str
    fecha_creacion: datetime
    tables: list[TableSummaryOut]
