from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.models import User
from app.schemas.schemas import User as UserSchema, UserUpdate
from app.core.security import get_password_hash
from app.db.session import get_db
from datetime import datetime

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    if user_in.email and user_in.email != current_user.email:
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
    
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/company/{company_id}", response_model=List[UserSchema])
async def read_users_by_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all users in a company.
    """
    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access users from other companies"
        )
    
    result = await db.execute(
        select(User)
        .where(User.company_id == company_id)
        .where(User.deleted_at.is_(None))
    )
    return result.scalars().all()

@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Delete a user (admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user.deleted_at = datetime.utcnow()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.put("/{user_id}/giveable-points", response_model=UserSchema)
async def update_user_points(
    user_id: int,
    points: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Update user's giveable points (admin only).
    """
    if points < 0:
        raise HTTPException(
            status_code=400,
            detail="Points cannot be negative"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user.giveable_points = points
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user 