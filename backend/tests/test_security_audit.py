import pytest
from pydantic import ValidationError
from starlette.testclient import TestClient
from app.config import Settings, INSECURE_DEV_SECRET
from app.schemas.auth import UserRegisterRequest, PasswordChangeRequest
from app.security.jwt import create_access_token, decode_access_token
from app.utils.rate_limiter import InMemoryRateLimiter


def test_production_secret_key_validation():
    # Production with default insecure key must fail
    with pytest.raises(ValueError, match="CRITICAL SECURITY CONFIGURATION"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=INSECURE_DEV_SECRET,
            _env_file=None
        )

    # Production with short key (< 32 chars) must fail
    with pytest.raises(ValueError, match="CRITICAL SECURITY CONFIGURATION"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short-secret-key",
            _env_file=None
        )

    # Production with wildcard CORS must fail
    with pytest.raises(ValueError, match="CORS_ORIGINS must not contain wildcard"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a-very-secure-production-secret-key-that-is-long-enough",
            CORS_ORIGINS=["*"],
            _env_file=None
        )

    # Valid production settings pass
    valid_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a-very-secure-production-secret-key-that-is-long-enough",
        CORS_ORIGINS=["https://myresumeapp.com"],
        _env_file=None
    )
    assert valid_settings.ENVIRONMENT == "production"


def test_development_allows_default_secrets():
    dev_settings = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="dev-insecure-secret-key-change-in-production-only-32chars",
        _env_file=None
    )
    assert dev_settings.ENVIRONMENT == "development"


def test_password_complexity_validation():
    # Valid strong password
    req = UserRegisterRequest(
        email="testpass@example.com",
        password="ValidPassword123!",
        full_name="Valid User"
    )
    assert req.password == "ValidPassword123!"

    # Missing uppercase
    with pytest.raises(ValidationError, match="uppercase"):
        UserRegisterRequest(
            email="testpass@example.com",
            password="alllowercase123!",
            full_name="Valid User"
        )

    # Missing lowercase
    with pytest.raises(ValidationError, match="lowercase"):
        UserRegisterRequest(
            email="testpass@example.com",
            password="ALLLOWERCASE123!",
            full_name="Valid User"
        )

    # Missing number or symbol
    with pytest.raises(ValidationError, match="digit or special character"):
        UserRegisterRequest(
            email="testpass@example.com",
            password="OnlyLettersNoNumber",
            full_name="Valid User"
        )

    # Too short (< 8 chars)
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="testpass@example.com",
            password="Sh1!",
            full_name="Valid User"
        )


def test_password_change_cannot_match_current(client: TestClient, test_user_a, auth_headers_user_a):
    response = client.put(
        "/api/v1/auth/password",
        headers=auth_headers_user_a,
        json={
            "current_password": "StrongPassword123!",
            "new_password": "StrongPassword123!"
        }
    )
    assert response.status_code == 400
    assert "cannot be identical" in response.json()["detail"]


def test_jwt_claims_and_iat():
    token = create_access_token({"sub": "42"})
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert "iat" in decoded
    assert "exp" in decoded
    assert decoded["exp"] > decoded["iat"]


def test_rate_limiter_logic():
    limiter = InMemoryRateLimiter()
    key = "test_user_key"
    
    # Allow 3 requests within 60s
    allowed_1, _ = limiter.is_rate_limited(key, max_requests=3, window_seconds=60)
    allowed_2, _ = limiter.is_rate_limited(key, max_requests=3, window_seconds=60)
    allowed_3, _ = limiter.is_rate_limited(key, max_requests=3, window_seconds=60)
    assert not allowed_1
    assert not allowed_2
    assert not allowed_3

    # 4th request must be rate limited
    is_limited, retry_after = limiter.is_rate_limited(key, max_requests=3, window_seconds=60)
    assert is_limited is True
    assert retry_after > 0

    # Reset clears history
    limiter.reset()
    is_limited_after_reset, _ = limiter.is_rate_limited(key, max_requests=3, window_seconds=60)
    assert is_limited_after_reset is False


def test_endpoint_rate_limiting_integration(client: TestClient):
    # Set a tiny rate limit check by hitting /api/v1/auth/login multiple times
    # In config, RATE_LIMIT_AUTH_PER_MINUTE is 10.
    status_codes = []
    for _ in range(12):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": "fake@example.com", "password": "WrongPassword123!"}
        )
        status_codes.append(resp.status_code)

    # At least one request should have received 429
    assert 429 in status_codes
    rate_limited_resp = [c for c in status_codes if c == 429]
    assert len(rate_limited_resp) >= 2
