"""Excel processing and persistence service.

Handles the full pipeline:
  1. Parse Excel via pandas (all sheets)
  2. Per sheet: create Tabla → infer types → create Columnas → batch-insert Filas
  3. Single commit with flushes for IDs

Shared parsing logic lives in the private `_parse_excel_sheets` helper.
"""

import numpy as np
import pandas as pd
from io import BytesIO
from typing import Any
from sqlalchemy.orm import Session

from models import Usuario, Proyecto, Tabla, Columna, Fila


# ---------------------------------------------------------------------------
# Type inference helpers
# ---------------------------------------------------------------------------

def infer_column_type(series: pd.Series) -> str:
    """Infer the logical type of a DataFrame column.

    Precedence:
        datetime64 / timedelta64 → "date"
        int64 / float64          → "number"
        else: try parsing sample as date → "date"
              try parsing sample as number → "number"
              fallback → "string"
    """
    dtype = series.dtype

    if pd.api.types.is_datetime64_any_dtype(dtype) or pd.api.types.is_timedelta64_dtype(dtype):
        return "date"

    if pd.api.types.is_numeric_dtype(dtype):
        return "number"

    sample = series.dropna().head(100)
    if len(sample) == 0:
        return "string"

    try:
        pd.to_datetime(sample, infer_datetime_format=True)
        return "date"
    except (ValueError, TypeError):
        pass

    try:
        numeric = pd.to_numeric(sample)
        if numeric.notna().all():
            return "number"
    except (ValueError, TypeError):
        pass

    return "string"


def sanitize_value(value: Any) -> Any:
    """Convert a cell value for JSONB storage.

    - NaN / NaT / None → None
    - pandas Timestamp → ISO 8601 string
    - numpy int/float → native Python int/float
    - everything else → as-is
    """
    if value is None:
        return None
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


# ---------------------------------------------------------------------------
# Private helper — shared Excel parsing logic (zero duplication)
# ---------------------------------------------------------------------------

def _parse_excel_sheets(db: Session, project_id: int, file_bytes: bytes) -> list[dict]:
    """Parse an Excel file and persist all sheets for a given project.

    This is the shared core used by both `create_project` and
    `add_sheets_to_project` — eliminating the previous duplication.

    Args:
        db: SQLAlchemy session.
        project_id: The project ID to associate tables with.
        file_bytes: Raw Excel file content.

    Returns:
        A list of table summary dicts (table_id, sheet_name, columns, row_count).

    Raises:
        ValueError: If the file is invalid or has no data.
    """
    try:
        sheets: dict[str, pd.DataFrame] = pd.read_excel(
            BytesIO(file_bytes), sheet_name=None, engine="openpyxl"
        )
    except Exception as exc:
        raise ValueError(f"Invalid Excel file: {exc}") from exc

    if not sheets:
        raise ValueError("No sheets found in the uploaded file")

    tables_summary = []

    for sheet_name, df in sheets.items():
        if df.empty and df.columns.empty:
            continue

        tabla = Tabla(proyecto_id=project_id, nombre_hoja=sheet_name)
        db.add(tabla)
        db.flush()

        col_types: dict[str, str] = {}
        for col_name in df.columns:
            col_type = infer_column_type(df[col_name])
            col_types[str(col_name)] = col_type
            columna = Columna(
                tabla_id=tabla.id,
                nombre=str(col_name),
                tipo=col_type,
            )
            db.add(columna)

        db.flush()

        col_names_str = [str(c) for c in df.columns]
        for row_idx, (_, row) in enumerate(df.iterrows()):
            row_data = {}
            for col_name in col_names_str:
                row_data[col_name] = sanitize_value(row[col_name])

            fila = Fila(
                tabla_id=tabla.id,
                orden=row_idx,
                data=row_data,
            )
            db.add(fila)

        db.flush()

        tables_summary.append({
            "table_id": tabla.id,
            "sheet_name": sheet_name,
            "columns": [
                {"name": name, "type": col_types[name]}
                for name in col_names_str
            ],
            "row_count": len(df),
        })

    if not tables_summary:
        raise ValueError("No data found in any sheet")

    return tables_summary


# ---------------------------------------------------------------------------
# Public API — project & table operations
# ---------------------------------------------------------------------------

def create_project(db: Session, user_id: int, filename: str, file_bytes: bytes) -> dict:
    """Create a new project for a user and parse the uploaded Excel file.

    Args:
        db: SQLAlchemy session.
        user_id: The user's database ID.
        filename: Original filename from the upload.
        file_bytes: Raw Excel file content.

    Returns:
        A dict with user_id, project_id, and a list of table summaries.

    Raises:
        ValueError: If the user does not exist or the file is invalid.
    """
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise ValueError("User not found")

    proyecto = Proyecto(usuario_id=user_id, nombre_archivo=filename)
    db.add(proyecto)
    db.flush()
    project_id = proyecto.id

    tables_summary = _parse_excel_sheets(db, project_id, file_bytes)

    db.commit()

    return {
        "user_id": user_id,
        "project_id": project_id,
        "tables": tables_summary,
    }


def add_sheets_to_project(db: Session, project_id: int, file_bytes: bytes) -> dict:
    """Upload additional sheets into an existing project.

    Args:
        db: SQLAlchemy session.
        project_id: The existing project's database ID.
        file_bytes: Raw Excel file content.

    Returns:
        A dict with project_id and a list of new table summaries.

    Raises:
        ValueError: If the project does not exist or the file is invalid.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None:
        raise ValueError("Project not found")

    tables_summary = _parse_excel_sheets(db, project_id, file_bytes)

    db.commit()

    return {
        "project_id": project_id,
        "tables": tables_summary,
    }


def list_user_projects(db: Session, user_id: int) -> list[dict]:
    """List all projects for a user with table counts.

    Args:
        db: SQLAlchemy session.
        user_id: The user's database ID.

    Returns:
        A list of dicts matching ProjectSummary schema.

    Raises:
        ValueError: If the user does not exist.
    """
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise ValueError("User not found")

    proyectos = (
        db.query(Proyecto)
        .filter(Proyecto.usuario_id == user_id)
        .order_by(Proyecto.fecha_creacion.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "nombre_archivo": p.nombre_archivo,
            "fecha_creacion": p.fecha_creacion,
            "tabla_count": len(p.tablas),
        }
        for p in proyectos
    ]


def get_project_detail(db: Session, project_id: int) -> dict:
    """Get full project detail including lightweight table summaries.

    Args:
        db: SQLAlchemy session.
        project_id: The project's database ID.

    Returns:
        A dict matching ProjectDetail schema.

    Raises:
        ValueError: If the project does not exist.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None:
        raise ValueError("Project not found")

    return {
        "id": proyecto.id,
        "nombre_archivo": proyecto.nombre_archivo,
        "fecha_creacion": proyecto.fecha_creacion,
        "dashboard_config": proyecto.dashboard_config,
        "tables": [
            {
                "id": t.id,
                "nombre_hoja": t.nombre_hoja,
                "row_count": len(t.filas),
                "column_count": len(t.columnas),
            }
            for t in proyecto.tablas
        ],
    }


def rename_project(db: Session, project_id: int, new_name: str) -> dict:
    """Rename a project.

    Args:
        db: SQLAlchemy session.
        project_id: The project's database ID.
        new_name: The new filename for the project.

    Returns:
        A dict matching ProjectDetail schema.

    Raises:
        ValueError: If the project does not exist.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None:
        raise ValueError("Project not found")

    proyecto.nombre_archivo = new_name
    db.commit()

    # Refresh to get updated state
    db.refresh(proyecto)

    return {
        "id": proyecto.id,
        "nombre_archivo": proyecto.nombre_archivo,
        "fecha_creacion": proyecto.fecha_creacion,
        "tables": [
            {
                "id": t.id,
                "nombre_hoja": t.nombre_hoja,
                "row_count": len(t.filas),
                "column_count": len(t.columnas),
            }
            for t in proyecto.tablas
        ],
        "dashboard_config": proyecto.dashboard_config,
    }


def delete_project(db: Session, project_id: int) -> None:
    """Delete a project and cascade all related tables, columns, and rows.

    Args:
        db: SQLAlchemy session.
        project_id: The project's database ID.

    Raises:
        ValueError: If the project does not exist.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None:
        raise ValueError("Project not found")

    db.delete(proyecto)
    db.commit()


def get_single_table(db: Session, table_id: int) -> dict:
    """Get full data for a single table (columns + rows).

    Args:
        db: SQLAlchemy session.
        table_id: The table's database ID.

    Returns:
        A dict matching SingleTableResponse schema.

    Raises:
        ValueError: If the table does not exist.
    """
    tabla = db.query(Tabla).filter(Tabla.id == table_id).first()
    if tabla is None:
        raise ValueError("Table not found")

    columns = [
        {"id": col.id, "name": col.nombre, "type": col.tipo}
        for col in tabla.columnas
    ]
    rows = [
        {"id": fila.id, "data": fila.data}
        for fila in tabla.filas
    ]

    return {
        "id": tabla.id,
        "sheet_name": tabla.nombre_hoja,
        "columns": columns,
        "rows": rows,
    }


def delete_table(db: Session, table_id: int) -> None:
    """Delete a single table and cascade its columns and rows.

    Args:
        db: SQLAlchemy session.
        table_id: The table's database ID.

    Raises:
        ValueError: If the table does not exist.
    """
    tabla = db.query(Tabla).filter(Tabla.id == table_id).first()
    if tabla is None:
        raise ValueError("Table not found")

    db.delete(tabla)
    db.commit()


def get_project_tables_full(db: Session, project_id: int) -> list[dict]:
    """Get full table data (columns + rows) for a specific project.

    Args:
        db: SQLAlchemy session.
        project_id: The project's database ID.

    Returns:
        A list of dicts matching SingleTableResponse schema.

    Raises:
        ValueError: If the project does not exist.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None:
        raise ValueError("Project not found")

    tables_detail = []
    for tabla in proyecto.tablas:
        columns = [
            {"id": col.id, "name": col.nombre, "type": col.tipo}
            for col in tabla.columnas
        ]
        rows = [
            {"id": fila.id, "data": fila.data}
            for fila in tabla.filas
        ]
        tables_detail.append({
            "id": tabla.id,
            "sheet_name": tabla.nombre_hoja,
            "columns": columns,
            "rows": rows,
        })

    return tables_detail


