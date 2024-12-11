from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.api import deps
from app.models.models import User, PointsTransaction, PointsRecipient
from app.schemas.schemas import Transaction
from app.core.constants import TransactionType
from app.db.session import get_db

router = APIRouter()

@router.get("/balance", response_model=dict)
async def get_points_balance(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's points balance.
    """
    return {
        "giveable_points": current_user.giveable_points,
        "redeemable_points": current_user.redeemable_points
    }

@router.get("/history/sent", response_model=List[Transaction])
async def get_sent_points_history(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get points transactions history where current user is sender.
    """
    result = await db.execute(
        select(PointsTransaction)
        .where(PointsTransaction.sender_id == current_user.id)
        .order_by(PointsTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/history/received", response_model=List[Transaction])
async def get_received_points_history(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get points transactions history where current user is recipient.
    """
    result = await db.execute(
        select(PointsTransaction)
        .join(PointsRecipient)
        .where(PointsRecipient.recipient_id == current_user.id)
        .order_by(PointsTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/company/{company_id}/transactions", response_model=List[Transaction])
async def get_company_transactions(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Get all points transactions in a company (admin only).
    """
    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access transactions from other companies"
        )
    
    result = await db.execute(
        select(PointsTransaction)
        .join(User, PointsTransaction.sender_id == User.id)
        .where(User.company_id == company_id)
        .order_by(PointsTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/admin-adjustment", response_model=Transaction)
async def create_admin_adjustment(
    user_id: int,
    points: int,
    notes: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Create an admin points adjustment (admin only).
    """
    # Get target user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create transaction
    transaction = PointsTransaction(
        sender_id=current_user.id,
        transaction_type=TransactionType.ADMIN_ADJUSTMENT,
        points=abs(points),
        admin_notes=notes
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    # Create recipient and update points
    recipient = PointsRecipient(
        transaction_id=transaction.id,
        recipient_id=user_id,
        points_amount=abs(points)
    )
    db.add(recipient)
    
    # Update user's points
    if points > 0:
        user.giveable_points += points
    else:
        user.giveable_points = max(0, user.giveable_points + points)
    
    db.add(user)
    await db.commit()
    
    return transaction 