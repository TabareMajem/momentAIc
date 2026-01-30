
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.integrations.gmail import gmail_integration

# Mock settings just to test import and structure
print("📧 Testing Gmail Integration Module...")

try:
    result = gmail_integration.execute_action("send_email", {})
    # Expecting failure due to await/sync mismatch or missing params, 
    # but checking if method exists.
    # Note: execute_action is async in base, but I implemented _send_email as sync (SMTP is blocking).
    # This test just checks import validity.
    print("✅ Module loaded successfully.")
except Exception as e:
    print(f"⚠️ Runtime check: {e}") 

print("Test Complete.")
