import pytest
from fastapi import Request, HTTPException
from unittest.mock import AsyncMock, patch
from app.utils.rate_limiter import rate_limit

class DummyRequest:
    def __init__(self, host="127.0.0.1"):
        self.client = type("Client", (), {"host": host})()

@pytest.mark.asyncio
@patch("app.utils.rate_limiter.r")
async def test_authenticated_user_under_limit(mock_redis):
    request = DummyRequest()
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zcard = AsyncMock(return_value=5)
    mock_redis.zadd = AsyncMock()
    mock_redis.expire = AsyncMock()

    await rate_limit(request, user_id="user123")

@pytest.mark.asyncio
@patch("app.utils.rate_limiter.r")
async def test_authenticated_user_exceeds_limit(mock_redis):
    request = DummyRequest()
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zcard = AsyncMock(return_value=10)
    mock_redis.zadd = AsyncMock()
    mock_redis.expire = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await rate_limit(request, user_id="user123")
    assert exc.value.status_code == 429

@pytest.mark.asyncio
@patch("app.utils.rate_limiter.r")
async def test_anonymous_user_under_limit(mock_redis):
    request = DummyRequest()
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zcard = AsyncMock(return_value=1)
    mock_redis.zadd = AsyncMock()
    mock_redis.expire = AsyncMock()

    await rate_limit(request, user_id=None)

@pytest.mark.asyncio
@patch("app.utils.rate_limiter.r")
async def test_anonymous_user_exceeds_limit(mock_redis):
    request = DummyRequest()
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zcard = AsyncMock(return_value=2)
    mock_redis.zadd = AsyncMock()
    mock_redis.expire = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await rate_limit(request, user_id=None)
    assert exc.value.status_code == 429
