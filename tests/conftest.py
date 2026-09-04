import pytest
import os
from database import Base, engine, init_db
from orchestrator.security import default_rate_limiter

@pytest.fixture(scope="session", autouse=True)
def setup_test_database_schema():
    """
    Creates database schema ONCE per test session for performance and stability.
    """
    try:
        init_db()
    except Exception:
        pass
    yield

@pytest.fixture(autouse=True)
def reset_rate_limits():
    """
    Resets rate limits before each test function for test isolation.
    """
    default_rate_limiter.reset()
    yield
    default_rate_limiter.reset()
