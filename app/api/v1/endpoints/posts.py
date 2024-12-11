from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api import deps
from app.models.models import Post, User, PointsTransaction, PointsRecipient, PostLike
from app.schemas.schemas import Post as PostSchema, PostTransactionCreate
from app.core.constants import TransactionType
from app.db.session import get_db

router = APIRouter()

@router.post("", response_model=PostSchema)
async def create_post(
    *,
    db: AsyncSession = Depends(get_db),
    post_in: PostTransactionCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new recognition post with points distribution.
    """
    # Validate total points
    total_points = sum(recipient.points for recipient in post_in.recipients)
    if total_points > current_user.giveable_points:
        raise HTTPException(
            status_code=400,
            detail="Not enough points available"
        )
    
    # Validate recipients are from same company
    for recipient in post_in.recipients:
        result = await db.execute(select(User).where(User.id == recipient.user_id))
        user = result.scalar_one_or_none()
        if not user or user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid recipient: {recipient.user_id}"
            )
    
    # Create post
    post = Post(
        content=post_in.content,
        author_id=current_user.id,
        total_points=total_points
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    # Create transaction
    transaction = PointsTransaction(
        sender_id=current_user.id,
        transaction_type=TransactionType.RECOGNITION,
        points=total_points,
        post_id=post.id
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    # Create recipients and update points
    for recipient_data in post_in.recipients:
        recipient = PointsRecipient(
            transaction_id=transaction.id,
            recipient_id=recipient_data.user_id,
            points_amount=recipient_data.points
        )
        db.add(recipient)
        
        result = await db.execute(select(User).where(User.id == recipient_data.user_id))
        user = result.scalar_one_or_none()
        user.redeemable_points += recipient_data.points
        db.add(user)
    
    # Update sender's points
    current_user.giveable_points -= total_points
    db.add(current_user)
    
    await db.commit()
    return post

@router.get("/company/{company_id}", response_model=List[PostSchema])
async def read_company_posts(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all posts in a company.
    """
    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access posts from other companies"
        )
    
    result = await db.execute(
        select(Post)
        .join(User, Post.author_id == User.id)
        .where(User.company_id == company_id)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{post_id}/like", response_model=PostSchema)
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Like a post.
    """
    # Check if post exists and is from same company
    result = await db.execute(
        select(Post)
        .join(User, Post.author_id == User.id)
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_author = await db.get(User, post.author_id)
    if post_author.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if already liked
    result = await db.execute(
        select(PostLike)
        .where(PostLike.post_id == post_id)
        .where(PostLike.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Post already liked"
        )
    
    # Create like
    like = PostLike(post_id=post_id, user_id=current_user.id)
    db.add(like)
    await db.commit()
    
    return post

@router.delete("/{post_id}/like", response_model=PostSchema)
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Unlike a post.
    """
    result = await db.execute(
        select(PostLike)
        .where(PostLike.post_id == post_id)
        .where(PostLike.user_id == current_user.id)
    )
    like = result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(
            status_code=400,
            detail="Post not liked"
        )
    
    await db.delete(like)
    await db.commit()
    
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none() 