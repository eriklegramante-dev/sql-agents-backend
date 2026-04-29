import pytest
from fastapi import HTTPException
from jose import jwt

from app.security.authenticator import JWTAuthenticator


def test_create_and_verify_access_token(fake_logger):
    authenticator = JWTAuthenticator(
        secret_key="secret",
        algorithm="HS256",
        exp_minutes=30,
        logger=fake_logger,
    )

    token = authenticator.create_access_token("123")

    assert authenticator.verify_token(token) == 123


def test_verify_token_rejects_missing_subject(fake_logger):
    authenticator = JWTAuthenticator(
        secret_key="secret",
        algorithm="HS256",
        exp_minutes=30,
        logger=fake_logger,
    )
    token = jwt.encode({"name": "user"}, "secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        authenticator.verify_token(token)

    assert exc.value.status_code == 401


def test_verify_token_rejects_invalid_token(fake_logger):
    authenticator = JWTAuthenticator(
        secret_key="secret",
        algorithm="HS256",
        exp_minutes=30,
        logger=fake_logger,
    )

    with pytest.raises(HTTPException) as exc:
        authenticator.verify_token("invalid")

    assert exc.value.status_code == 401
