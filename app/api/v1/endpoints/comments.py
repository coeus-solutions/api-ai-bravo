from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.models import Comment, User, Post, CommentLike, PointsTransaction, PointsRecipient
from app.schemas.schemas import Comment as CommentSchema, CommentTransactionCreate
from app.core.constants import TransactionType
from app.db.session import get_db

router = APIRouter()

@router.post("", response_model=CommentSchema)
async def create_comment(
    *,
    db: AsyncSession = Depends(get_db),
    comment_in: CommentTransactionCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new comment with optional points distribution.
    """
    # Validate post exists and is from same company
    result = await db.execute(
        select(Post)
        .join(User, Post.author_id == User.id)
        .where(Post.id == comment_in.post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_author = await db.get(User, post.author_id)
    if post_author.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Calculate total points if any
    total_points = sum(recipient.points for recipient in comment_in.recipients)
    
    # Validate points if distributing
    if total_points > 0:
        if total_points > current_user.giveable_points:
            raise HTTPException(
                status_code=400,
                detail="Not enough points available"
            )
        
        # Validate recipients are from same company
        for recipient in comment_in.recipients:
            result = await db.execute(select(User).where(User.id == recipient.user_id))
            user = result.scalar_one_or_none()
            if not user or user.company_id != current_user.company_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid recipient: {recipient.user_id}"
                )
    
    # Create comment
    comment = Comment(
        content=comment_in.content,
        post_id=comment_in.post_id,
        author_id=current_user.id,
        total_points=total_points
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    # Handle points distribution if any
    if total_points > 0:
        # Create transaction
        transaction = PointsTransaction(
            sender_id=current_user.id,
            transaction_type=TransactionType.COMMENT_RECOGNITION,
            points=total_points,
            comment_id=comment.id
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        
        # Create recipients and update points
        for recipient_data in comment_in.recipients:
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
    
    return comment

@router.get("/post/{post_id}", response_model=List[CommentSchema])
async def read_post_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all comments for a post.
    """
    # Verify post exists and user has access
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
    
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{comment_id}/like", response_model=CommentSchema)
async def like_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Like a comment.
    """
    # Check if comment exists and is from same company
    result = await db.execute(
        select(Comment)
        .join(Post, Comment.post_id == Post.id)
        .join(User, Post.author_id == User.id)
        .where(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    post = await db.get(Post, comment.post_id)
    post_author = await db.get(User, post.author_id)
    if post_author.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if already liked
    result = await db.execute(
        select(CommentLike)
        .where(CommentLike.comment_id == comment_id)
        .where(CommentLike.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Comment already liked"
        )
    
    # Create like
    like = CommentLike(comment_id=comment_id, user_id=current_user.id)
    db.add(like)
    await db.commit()
    
    return comment

@router.delete("/{comment_id}/like", response_model=CommentSchema)
async def unlike_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Unlike a comment.
    """
    result = await db.execute(
        select(CommentLike)
        .where(CommentLike.comment_id == comment_id)
        .where(CommentLike.user_id == current_user.id)
    )
    like = result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(
            status_code=400,
            detail="Comment not liked"
        )
    
    await db.delete(like)
    await db.commit()
    
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    return result.scalar_one_or_none() 