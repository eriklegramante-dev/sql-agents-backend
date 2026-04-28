from app.security.hashing import PasswordManager


class RaisingContext:
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise RuntimeError("failure")


def test_hash_and_verify_password(fake_logger):
    manager = PasswordManager(logger=fake_logger)

    hashed = manager.hash_password("Strong@123")

    assert hashed != "Strong@123"
    assert manager.verify_password("Strong@123", hashed) is True
    assert manager.verify_password("Wrong@123", hashed) is False


def test_verify_password_returns_false_when_context_raises(fake_logger):
    manager = PasswordManager(logger=fake_logger)
    manager.pwd_context = RaisingContext()

    assert manager.verify_password("Strong@123", "hash") is False
