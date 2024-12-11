# Recognition Platform

A web-based recognition platform that enables company employees to appreciate each other through a points-based system.

## Features

- User Authentication (signup, login)
- Role-based access control (admin, member)
- Points system for peer recognition
- Recognition posts with points distribution
- Comments with optional points distribution
- Like system for posts and comments
- Points transaction history
- Company-based isolation of data

## Tech Stack

- FastAPI (Python 3.8+)
- PostgreSQL
- SQLAlchemy (async)
- Pydantic
- JWT Authentication

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd recognition-platform
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a PostgreSQL database:
```bash
createdb recognition_platform
```

5. Copy the `.env.example` file to `.env` and update the values:
```bash
cp .env.example .env
```

6. Initialize the database:
```bash
alembic upgrade head
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. The API will be available at `http://localhost:8000`
3. API documentation will be available at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- POST `/api/v1/auth/signup` - Create new user
- POST `/api/v1/auth/login` - Login user
- POST `/api/v1/auth/test-token` - Test authentication

### Users
- GET `/api/v1/users/me` - Get current user
- PUT `/api/v1/users/me` - Update current user
- GET `/api/v1/users/company/{company_id}` - Get company users
- DELETE `/api/v1/users/{user_id}` - Delete user (admin)
- PUT `/api/v1/users/{user_id}/giveable-points` - Update user points (admin)

### Posts
- POST `/api/v1/posts` - Create recognition post
- GET `/api/v1/posts/company/{company_id}` - Get company posts
- POST `/api/v1/posts/{post_id}/like` - Like post
- DELETE `/api/v1/posts/{post_id}/like` - Unlike post

### Comments
- POST `/api/v1/comments` - Create comment
- GET `/api/v1/comments/post/{post_id}` - Get post comments
- POST `/api/v1/comments/{comment_id}/like` - Like comment
- DELETE `/api/v1/comments/{comment_id}/like` - Unlike comment

### Points
- GET `/api/v1/points/balance` - Get points balance
- GET `/api/v1/points/history/sent` - Get sent points history
- GET `/api/v1/points/history/received` - Get received points history
- GET `/api/v1/points/company/{company_id}/transactions` - Get company transactions (admin)
- POST `/api/v1/points/admin-adjustment` - Create admin points adjustment (admin)

## Security

- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Company-based data isolation
- Input validation with Pydantic
- Rate limiting
- CORS configuration

## Development

The project uses:
- Black for code formatting
- Flake8 for linting
- Pytest for testing
- Alembic for database migrations

## License

MIT License 