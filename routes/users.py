"""User management routes.

POST   /api/users          — get-or-create user by name
GET    /api/users/{user_id} — get user by ID
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import ValidationError

from database import get_db
from schemas import UserCreate, UserResponse
from services.user_service import get_or_create_user, get_user

router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    """Get-or-create a user by name.

    If a user with the given nombre already exists, returns it.
    Otherwise creates a new user and returns it.
    """
    try:
        result = get_or_create_user(db, body.nombre)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return UserResponse(**result)


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    try:
        result = get_user(db, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return UserResponse(**result)
