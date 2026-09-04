import os
os.environ["DATABASE_URL"] = "sqlite:///./test_ion.db"

import pytest
from database import Base, engine, init_db
from orchestrator.security import default_rate_limiter

@pytest.fixture(autouse=True)
def reset_database_tables():
    """
    Clears test_ion.db database tables before each test function for total test isolation.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
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
