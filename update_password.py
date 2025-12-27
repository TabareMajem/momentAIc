#!/usr/bin/env python3
"""Update user password hash directly in the database"""
import asyncio
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
import os

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://momentaic:CHANGE_ME@postgres:5432/momentaic")
# Convert async URL to sync
SYNC_DB_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_hash = pwd.hash("Cruyff14_88")
print(f"Generated hash: {new_hash}")

from sqlalchemy import create_engine
engine = create_engine(SYNC_DB_URL)

with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE users SET hashed_password = :hash WHERE email = :email"),
        {"hash": new_hash, "email": "tabaremajem@gmail.com"}
    )
    conn.commit()
    print(f"Rows updated: {result.rowcount}")

# Verify
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT hashed_password FROM users WHERE email = :email"),
        {"email": "tabaremajem@gmail.com"}
    )
    row = result.fetchone()
    print(f"New hash in DB: {row[0]}")
