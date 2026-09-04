import pytest
from database import Base, engine, init_db
from orchestrator.security import default_rate_limiter

@pytest.fixture(autouse=True)
def reset_database_and_rate_limits():
    """
    Resets database tables and rate limits before each test run for strict test isolation.
    """
    default_rate_limiter.reset()
    try:
        Base.metadata.drop_all(bind=engine, checkfirst=True)
    except Exception:
        pass
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception:
        pass
    yield
    default_rate_limiter.reset()
