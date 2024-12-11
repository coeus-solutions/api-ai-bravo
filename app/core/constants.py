from enum import Enum

# User related constants
INITIAL_GIVEABLE_POINTS = 50
INITIAL_REDEEMABLE_POINTS = 0

class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class TransactionType(str, Enum):
    RECOGNITION = "recognition"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    INITIAL_ALLOCATION = "initial_allocation"
    COMMENT_RECOGNITION = "comment_recognition"

# Authentication constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "${YOUR_SECRET_KEY}"  # Should be loaded from environment variables

# API Rate limiting
RATE_LIMIT_PER_MINUTE = 100

# Performance constants
MAX_CONCURRENT_USERS = 1000
PAGE_SIZE = 20

# Database constants
DB_CONNECTION_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30

# Points system constants
MIN_POINTS_PER_RECOGNITION = 1
MAX_POINTS_PER_RECOGNITION = 100

# Content constraints
MAX_POST_LENGTH = 1000
MAX_COMMENT_LENGTH = 500 