"""
Firebase Authentication Service
Handles verifying Firebase ID Tokens and bridging them with Momentaic Users.
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import structlog
import secrets
import firebase_admin
from firebase_admin import credentials, auth

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserTier, CreditTransaction
from app.schemas.auth import TokenPair, AuthResponse, UserResponse
from app.services.auth_service import AuthService

logger = structlog.get_logger()

# Initialize Firebase Admin if not already initialized
try:
    firebase_admin.get_app()
except ValueError:
    import os
    cred_path = os.path.join(os.getcwd(), 'firebase-adminsdk.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
    else:
        logger.warning(f"Firebase Admin SDK credentials not found at {cred_path}")

class FirebaseAuthService:
    """Firebase Authentication Bridge for Momentaic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)
        
    async def verify_and_login(self, id_token: str) -> AuthResponse:
        """
        Verifies a Firebase ID token and logs the user in.
        If the user does not exist, provisions a new Momentaic account.
        """
        from fastapi import HTTPException, status
        from fastapi.concurrency import run_in_threadpool
        
        try:
            logger.info("Starting verify_and_login for token")
            # Verify the token against Google's public keystore using a threadpool to avoid blocking async loop
            decoded_token = await run_in_threadpool(auth.verify_id_token, id_token, clock_skew_seconds=10)
            email = decoded_token.get('email')
            full_name = decoded_token.get('name', '')
            logger.info(f"Token verified successfully. Email: {email}")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Firebase ID token does not contain an email address."
                )
                
            email = email.lower()
            
            # Check if user exists in our DB
            logger.info("Checking if user exists in DB")
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            logger.info(f"DB check complete. User exists: {bool(user)}")
            
            if user:
                # User exists, log them in
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Account is deactivated"
                    )
                
                # Create Momentaic JWTs
                tokens = await self.auth_service._create_tokens(user)
                
                from datetime import datetime
                user.last_login_at = datetime.utcnow()
                await self.db.commit()
                
                logger.info("OAuth User logged in", user_id=str(user.id), email=user.email)
                
                return AuthResponse(
                    user=UserResponse.model_validate(user),
                    tokens=tokens,
                )
            
            else:
                # User does not exist, provision a new account
                logger.info("Provisioning new OAuth user", email=email)
                
                # Generate a secure random password since they login via OAuth
                random_password = secrets.token_urlsafe(32)
                
                initial_credits = settings.default_starter_credits
                
                # Auto-approve email verification if Firebase says it's verified (optional)
                is_verified = decoded_token.get('email_verified', False)
                
                new_user = User(
                    email=email,
                    hashed_password=get_password_hash(random_password),
                    full_name=full_name or email.split('@')[0],
                    tier=UserTier.STARTER,
                    credits_balance=initial_credits,
                    avatar_url=decoded_token.get('picture', f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}"),
                    is_verified=is_verified
                )
                
                self.db.add(new_user)
                await self.db.flush() # flush to get the UUID
                
                # Initial credit top-up log
                transaction = CreditTransaction(
                    user_id=new_user.id,
                    amount=initial_credits,
                    balance_after=initial_credits,
                    transaction_type="topup",
                    reason="Welcome bonus (OAuth)",
                )
                self.db.add(transaction)
                
                # Generate tokens
                tokens = await self.auth_service._create_tokens(new_user)
                await self.db.commit()
                
                logger.info("OAuth User registered", user_id=str(new_user.id), email=new_user.email)
                
                return AuthResponse(
                    user=UserResponse.model_validate(new_user),
                    tokens=tokens,
                )
                
        except firebase_admin.auth.InvalidIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase ID token"
            )
        except firebase_admin.auth.ExpiredIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase ID token has expired"
            )
        except Exception as e:
            logger.error("Firebase auth error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}"
            )
