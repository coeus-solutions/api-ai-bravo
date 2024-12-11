from setuptools import setup, find_packages

setup(
    name="recognition-platform",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "pydantic-settings",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "email-validator",
        "asyncpg",
        "alembic",
        "python-dotenv",
        "supabase",
    ],
) 