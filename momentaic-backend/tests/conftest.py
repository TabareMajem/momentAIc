"""
Pytest Configuration and Fixtures
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserTier
from app.models.startup import Startup, StartupStage


# Test database URL
TEST_DATABASE_URL = settings.database_url.replace(
    settings.database_url.split("/")[-1],
    "momentaic_test"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Test User",
        tier=UserTier.STARTER,
        credits_balance=100,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_growth(db_session: AsyncSession) -> User:
    """Create a test user with Growth tier"""
    user = User(
        id=uuid4(),
        email="growth@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Growth User",
        tier=UserTier.GROWTH,
        credits_balance=500,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_startup(db_session: AsyncSession, test_user: User) -> Startup:
    """Create a test startup"""
    startup = Startup(
        id=uuid4(),
        owner_id=test_user.id,
        name="Test Startup",
        tagline="Building the future",
        description="A test startup for unit tests",
        industry="Technology",
        stage=StartupStage.MVP,
        metrics={
            "mrr": 10000,
            "dau": 500,
            "burn_rate": 50000,
            "runway_months": 12,
        },
    )
    db_session.add(startup)
    await db_session.commit()
    await db_session.refresh(startup)
    return startup


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate auth headers for test user"""
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email, "tier": test_user.tier.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_growth(test_user_growth: User) -> dict:
    """Generate auth headers for growth user"""
    token = create_access_token(
        data={"sub": str(test_user_growth.id), "email": test_user_growth.email, "tier": test_user_growth.tier.value}
    )
    return {"Authorization": f"Bearer {token}"}


# Mock fixtures for external services
@pytest.fixture
def mock_llm(mocker):
    """Mock LLM responses"""
    mock_response = mocker.MagicMock()
    mock_response.content = "This is a mock AI response."
    
    mock_llm = mocker.MagicMock()
    mock_llm.ainvoke = mocker.AsyncMock(return_value=mock_response)
    
    mocker.patch("app.agents.base.get_llm", return_value=mock_llm)
    return mock_llm


@pytest.fixture
def mock_stripe(mocker):
    """Mock Stripe API"""
    mocker.patch("stripe.Customer.create", return_value=mocker.MagicMock(id="cus_test123"))
    mocker.patch("stripe.checkout.Session.create", return_value=mocker.MagicMock(
        id="cs_test123",
        url="https://checkout.stripe.com/test"
    ))
    mocker.patch("stripe.Subscription.retrieve", return_value=mocker.MagicMock(
        status="active",
        current_period_end=1735689600,
        cancel_at_period_end=False
    ))


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis"""
    mock_redis = mocker.AsyncMock()
    mock_redis.get = mocker.AsyncMock(return_value=None)
    mock_redis.set = mocker.AsyncMock(return_value=True)
    mock_redis.delete = mocker.AsyncMock(return_value=1)
    mock_redis.zremrangebyscore = mocker.AsyncMock(return_value=0)
    mock_redis.zcard = mocker.AsyncMock(return_value=5)
    mock_redis.zadd = mocker.AsyncMock(return_value=1)
    mock_redis.expire = mocker.AsyncMock(return_value=True)
    mock_redis.pipeline = mocker.MagicMock(return_value=mock_redis)
    mock_redis.execute = mocker.AsyncMock(return_value=[0, 5, 1, True])
    
    return mock_redis
