# Recognition Platform - Product Requirements Document

## Table of Contents
1. [Overview](#1-overview)
2. [Core Features](#2-core-features)
3. [Technical Requirements](#3-technical-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Development Phases](#5-development-phases)
6. [Success Metrics](#6-success-metrics)

## 1. Overview
A web-based recognition platform that enables company employees to appreciate each other through a points-based system. The platform focuses on simple user management and peer-to-peer recognition.

## 2. Core Features

### 2.1 User Authentication
#### Sign Up
- Users can create an account by providing:
  - Full name
  - Email address
  - Company name
- Email verification required for account activation
- Each user is associated with exactly one company

#### Login
- Users sign in using email and password
- Session management with secure token-based authentication

### 2.2 Role Management
#### Available Roles
- Admin
- Member

#### Role Permissions
**Admin Users:**
- Invite new users to their company
- Edit user profiles within their company
- Delete users from their company
- Create recognition posts and comments
- Award points to other users
- Modify giveable points for any user

**Member Users:**
- Create recognition posts and comments
- Award points to other users
- View and edit their own profile

### 2.3 Points System

#### Points Types
- **Giveable Points**
  - Used to recognize other users
  - Initial balance of 50 points for new users
  - Can be manually adjusted by admin users
  - Cannot be used for self-recognition
  - Can be distributed among multiple users in a single post or comment

- **Redeemable Points**
  - Earned when receiving recognition from other users
  - Accumulate over time
  - Cannot be used for giving recognition
  - Balance visible on user profile

#### Points Administration
- Admin users can:
  - View points history of all users
  - Modify giveable points balance
  - Generate points transaction reports
  - Set up automated points allocation rules

#### Points Transaction History
- All points transactions must be logged with:
  - Transaction ID
  - Sender user ID
  - Recipient user ID(s)
  - Points amount
  - Transaction type
  - Associated post/comment ID
  - Timestamp
  - Admin notes (for manual adjustments)

### 2.4 Recognition System

#### Posts
- Users can create recognition posts containing:
  - Text description (required)
  - Points allocation (required)
  - Multiple tagged users (required)
  - Points distribution among tagged users
  - Optional attachments
- Users can like/unlike posts
- Like count displayed on each post
- List of users who liked the post is accessible
- Users can see if they have liked a post
- System validates if user has sufficient giveable points
- Points are immediately deducted from sender and added to recipients

#### Comments
- Users can comment on recognition posts with:
  - Text response
  - Points allocation to multiple users (optional)
  - Multiple tagged users
- Users can like/unlike comments
- Like count displayed on each comment
- List of users who liked the comment is accessible
- Users can see if they have liked a comment
- Points validation for comment recognition
- Points distribution tracking for comments
- Comments without points allocation are allowed

## 3. Technical Requirements

### 3.1 Frontend (React.js)
- Component-based architecture
- State management using Redux
- Responsive design for mobile and desktop
- Real-time updates for notifications

### 3.2 Backend (FastAPI)
- RESTful API endpoints
- Async request handling
- JWT authentication
- Request validation
- Error handling middleware

### 3.3 Database (Supabase)

#### Tables

##### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    company_id INTEGER REFERENCES companies(id),
    role TEXT NOT NULL CHECK (role IN ('admin', 'member')),
    giveable_points INTEGER NOT NULL DEFAULT 50,
    redeemable_points INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT positive_points CHECK (giveable_points >= 0 AND redeemable_points >= 0)
);
```

##### Companies
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

##### Points Transactions
```sql
CREATE TABLE points_transactions (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id),
    transaction_type TEXT NOT NULL CHECK (
        transaction_type IN (
            'recognition', 
            'admin_adjustment', 
            'initial_allocation',
            'comment_recognition'
        )
    ),
    post_id INTEGER REFERENCES posts(id),
    comment_id INTEGER REFERENCES comments(id),
    points INTEGER NOT NULL,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

##### Points Recipients
```sql
CREATE TABLE points_recipients (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES points_transactions(id),
    recipient_id INTEGER REFERENCES users(id),
    points_amount INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT positive_points CHECK (points_amount > 0)
);
```

##### Recognition Posts
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    total_points INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT positive_points CHECK (total_points > 0)
);
```

##### Comments
```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    total_points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT points_non_negative CHECK (total_points >= 0)
);
```

##### Post Likes
```sql
CREATE TABLE post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(post_id, user_id)
);
```

##### Comment Likes
```sql
CREATE TABLE comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER REFERENCES comments(id),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(comment_id, user_id)
);
```

### 3.4 API Endpoints

#### Authentication
- POST /auth/signup
- POST /auth/login
- POST /auth/verify-email

#### User Management
- POST /users/invite
- PUT /users/{user_id}
- DELETE /users/{user_id}
- GET /users/company/{company_id}

#### Points Management
- GET /users/{user_id}/points-balance
- PUT /users/{user_id}/giveable-points (admin only)
- GET /users/{user_id}/points-history
- GET /companies/{company_id}/points-transactions

#### Recognition
- POST /posts
- GET /posts/company/{company_id}
- POST /posts/{post_id}/comments
- GET /posts/{post_id}/comments

#### Likes Management
- POST /posts/{post_id}/likes
- DELETE /posts/{post_id}/likes
- GET /posts/{post_id}/likes
- POST /comments/{comment_id}/likes
- DELETE /comments/{comment_id}/likes
- GET /comments/{comment_id}/likes

## 4. Non-Functional Requirements

### 4.1 Performance
- Page load time < 2 seconds
- API response time < 500ms
- Support for up to 1000 concurrent users

### 4.2 Security
- Password hashing using bcrypt
- HTTPS encryption
- Input sanitization
- Rate limiting on API endpoints

### 4.3 Scalability
- Horizontal scaling capability
- Database connection pooling
- Caching for frequently accessed data

### 4.4 Data Integrity
- Transaction consistency through database constraints
- Points balance validation before each transaction
- Audit trail for all points modifications
- Regular points reconciliation processes

## 5. Development Phases

### Phase 1: Core Features (Weeks 1-4)
- User authentication
- Role management
- Basic user management
- Points system database design

### Phase 2: Points System (Weeks 5-7)
- Points tracking and transaction history
- Multi-user recognition
- Admin points management
- Points validation logic

### Phase 3: Recognition System (Weeks 8-9)
- Posts creation with multi-user recognition
- Comments system with multi-user recognition
- Points distribution
- Like functionality for posts and comments

### Phase 4: Testing & Polish (Weeks 10-12)
- Integration testing
- Performance optimization
- UI/UX improvements
- Points system stress testing

## 6. Success Metrics
- User activation rate > 80%
- Daily active users
- Recognition posts per user per week
- Average points distributed per user
- Average points distributed per transaction
- Points utilization rate
- Number of multi-user recognitions
- Points distribution patterns
- Average likes per post
- Average likes per comment
- User engagement through likes
- Correlation between likes and points awarded
