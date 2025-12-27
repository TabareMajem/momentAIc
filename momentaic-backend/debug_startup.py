import sys
import os

# Mock environment variables to pass Pydantic validation
os.environ["SECRET_KEY"] = "mock_secret_key_needs_to_be_32_chars_long"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["JWT_SECRET_KEY"] = "mock_jwt_secret"

print("Attempting to import app.main...")
try:
    from app.main import app
    print("✅ SUCCESS: app.main imported successfully!")
except Exception as e:
    print(f"❌ CRASH: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
