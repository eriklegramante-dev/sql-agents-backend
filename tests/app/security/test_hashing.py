from app.security.hashing import PasswordManager


class RaisingContext:
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise RuntimeError("failure")


class FakeContext:
    def hash(self, password: str) -> str:
        return f"hashed::{password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed::{plain_password}"


def test_hash_and_verify_password(fake_logger):
    manager = PasswordManager(logger=fake_logger)

    manager.pwd_context = FakeContext()

    hashed = manager.hash_password("Strong@123")

    assert hashed == "hashed::Strong@123"

    assert (
        manager.verify_password(
            "Strong@123",
            hashed,
        )
        is True
    )

    assert (
        manager.verify_password(
            "Wrong@123",
            hashed,
        )
        is False
    )


def test_hash_password_logs_messages(fake_logger):
    manager = PasswordManager(logger=fake_logger)

    manager.pwd_context = FakeContext()

    hashed = manager.hash_password("Strong@123")

    assert hashed == "hashed::Strong@123"

    assert any(level == "info" for level, _ in fake_logger.messages)

    assert any(level == "debug" for level, _ in fake_logger.messages)


def test_verify_password_returns_false_when_context_raises(fake_logger):
    manager = PasswordManager(logger=fake_logger)
    manager.pwd_context = RaisingContext()

    assert manager.verify_password("Strong@123", "hash") is False


def test_verify_password_logs_error_when_context_raises(fake_logger):
    manager = PasswordManager(logger=fake_logger)
    manager.pwd_context = RaisingContext()

    result = manager.verify_password("Strong@123", "hash")

    assert result is False
    assert any(level == "error" for level, message in fake_logger.messages)


def test_password_manager_uses_default_logger_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    monkeypatch.setattr("app.security.hashing.LOGGER", fake_logger)

    manager = PasswordManager()

    assert manager.logger is fake_logger
