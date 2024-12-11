from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.session import get_db
from app.core.security import pwd_context
from app.models.models import User
from app.schemas.schemas import TokenPayload
from datetime import datetime
from sqlalchemy import select

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        # Debug: Print token
        print(f"Received token: {token[:10]}...")
        
        # Decode without verification first to check the token structure
        unverified_payload = jwt.get_unverified_claims(token)
        print(f"Unverified payload: {unverified_payload}")
        
        # Now decode with verification
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
            print(f"Verified payload: {payload}")
        except Exception as e:
            print(f"JWT decode error: {str(e)}")
            raise

        token_data = TokenPayload(**payload)
        print(f"Token data: {token_data}")
        
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise
        
    try:
        # Convert string subject back to integer for database lookup
        user_id = int(token_data.sub)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        print(f"Found user: {user is not None}")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user 