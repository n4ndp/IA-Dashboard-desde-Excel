"""Dashboard generation route.

POST /api/users/{user_id}/projects/{project_id}/generate-dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Proyecto
from services.excel_service import get_project_tables_full
from services.analytics_service import AnalyticsEngine
from services import ai_service
from schemas import GenerateDashboardResponse

router = APIRouter()


def _validate_ownership(db: Session, user_id: int, project_id: int) -> dict:
    """Validate user exists AND project belongs to that user.

    Returns the project detail dict on success.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == project_id).first()
    if proyecto is None or proyecto.usuario_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return proyecto


@router.post(
    "/users/{user_id}/projects/{project_id}/generate-dashboard",
    response_model=GenerateDashboardResponse,
)
def generate_dashboard_endpoint(
    user_id: int,
    project_id: int,
    db: Session = Depends(get_db),
):
    """Generate an AI-powered dashboard for the project's data."""
    # 1. Validate ownership
    proyecto = _validate_ownership(db, user_id, project_id)

    # 2. Fetch all tables with full data for context
    try:
        tables = get_project_tables_full(db, project_id)
    except ValueError:
        tables = []

    # 3. Check project has tables
    if not tables:
        raise HTTPException(
            status_code=400,
            detail="Project has no tables to analyze",
        )

    # 4. Build context for AI (table summaries with samples)
    tables_context = []
    for t in tables:
        sample_rows = [row["data"] for row in t.get("rows", [])[:5] if row.get("data")]
        tables_context.append({
            "id": t["id"],
            "sheet_name": t["sheet_name"],
            "columns": t["columns"],
            "row_count": len(t.get("rows", [])),
            "rows": sample_rows,
        })

    # 5. Create analytics engine and generate
    engine = AnalyticsEngine(db, project_id)

    try:
        config = ai_service.generate_dashboard(
            db=db,
            project_id=project_id,
            engine=engine,
            tables_context=tables_context,
        )
    except TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Dashboard generation timed out",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard generation failed: {exc}",
        )

    # 6. Save to project
    proyecto.dashboard_config = config
    db.flush()

    # 7. Return response
    return GenerateDashboardResponse(
        widgets=config.get("widgets", []),
        generated_at=config.get("generated_at"),
    )
