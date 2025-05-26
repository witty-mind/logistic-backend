import pytest
import asyncio
import os
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

# Original settings to be restored
original_db_url = os.getenv("DATABASE_URL")

# Attempt to set a test database URL
# In a real CI/local setup, this would point to a dedicated test DB.
# Here, we might just append "_test" or use an in-memory SQLite if PG features weren't critical.
# For now, let's assume we can change the DB name for the test session.
# This is highly dependent on the .env file and how settings are loaded.
# We will try to override it early.

TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db") + "_test"
os.environ["DATABASE_URL_OVERRIDE"] = TEST_DATABASE_URL # Signal to app.core.config to use this

# Re-import settings and app AFTER overriding env var.
# This is tricky because settings might be imported when other modules are.
# A robust way is to have app.core.config.py read this _OVERRIDE var.
# For now, we hope this override takes effect before app.core.config.settings is fully initialized by tests.
from app.core.config import settings
from app.db.base import Base 
from app.main import app # Import your FastAPI app
from app.db.session import get_db


# Ensure settings uses the override if present
# This logic should ideally be within app.core.config.py
if "DATABASE_URL_OVERRIDE" in os.environ:
    settings.DATABASE_URL = os.environ["DATABASE_URL_OVERRIDE"]


# Create a new async engine for the test database
test_engine = create_async_engine(settings.DATABASE_URL, echo=False) # Usually False for tests
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Override `get_db` dependency to use the test database session.
    """
    async with TestSessionLocal() as session:
        yield session

# Apply the override for all tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """
    Apply Alembic migrations at the start of the test session.
    Rollback or clean up is harder; typically, a fresh test DB is used.
    """
    print(f"Attempting to run migrations on TEST_DATABASE_URL: {settings.DATABASE_URL}")
    alembic_cfg = AlembicConfig("alembic.ini")
    
    # Point alembic to the test database URL
    # Alembic's env.py is configured to read from app.core.config.settings.DATABASE_URL
    # So, if settings.DATABASE_URL is correctly overridden, this should work.
    
    # Check if the database URL in alembic.ini needs to be temporarily changed
    # For simplicity, we rely on env.py correctly picking up the overridden settings.DATABASE_URL
    # alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL) # Might be needed if env.py doesn't see override

    try:
        alembic_command.upgrade(alembic_cfg, "head")
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Error applying migrations: {e}")
        # Depending on policy, either fail tests or proceed with caution
        # For now, we'll print error and let tests run, they will likely fail if DB is not setup.
        # raise # Optionally re-raise to stop tests if migrations are critical

    yield

    # Teardown: Drop all tables (or use a more sophisticated cleanup)
    # This is crucial for test isolation if the DB is persistent across test runs.
    # For now, this is commented out as it's complex and might fail in restricted env.
    # async def drop_all_tables_async():
    #     async with test_engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.drop_all)
    # asyncio.run(drop_all_tables_async())
    # print("Dropped all tables after test session.")


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a test database session for individual tests.
    Ensures the session is closed after the test.
    """
    async with TestSessionLocal() as session:
        yield session
        # Rollback any uncommitted changes after each test
        # await session.rollback() # Not strictly necessary if each test commits what it needs or is read-only

@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Test client for making API requests.
    Uses the FastAPI app with overridden dependencies.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Helper to get an authenticated client
@pytest.fixture(scope="function") # function scope to get fresh tokens if needed
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """
    Provides an AsyncClient that is authenticated for a test user.
    Registers and logs in a new unique user for each test function that uses it.
    """
    email = f"authtestuser_{uuid.uuid4().hex[:6]}@example.com"
    password = "TestPassword123"

    # Register user
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    
    # Log in user
    login_response = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token_data = login_response.json()
    access_token = token_data["access_token"]
    
    client.headers = {
        "Authorization": f"Bearer {access_token}",
        **client.headers
    }
    return client


# Restore original environment variables if they were changed
# This might not be robust enough if tests run in parallel or are interrupted.
# Using a context manager or a finalizer plugin for pytest might be better.
@pytest.fixture(scope="session", autouse=True)
def restore_env_vars():
    yield
    if original_db_url:
        os.environ["DATABASE_URL"] = original_db_url
    else:
        os.environ.pop("DATABASE_URL", None)
    os.environ.pop("DATABASE_URL_OVERRIDE", None)
