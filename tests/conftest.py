import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("APP_ENVIRONMENT", "dev")
os.environ.setdefault("DATABASE_URL_DEV", "postgresql+asyncpg://localhost/test_db")
os.environ.setdefault("DATABASE_URL_PROD", "")
os.environ.setdefault("SENTRY_DNS", "")
os.environ.setdefault("SECURITY_SECRET_KEY", "test-secret-key")
os.environ.setdefault("SECURITY_JWT_ALGORITHM", "HS256")
os.environ.setdefault("SECURITY_JWT_EXP_MINUTES", "60")

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


class FakeLogger:
    def __init__(self) -> None:
        self.messages = []

    def log_info(self, message: str) -> None:
        self.messages.append(("info", message))

    def log_debug(self, message: str) -> None:
        self.messages.append(("debug", message))

    def log_error(self, message: str) -> None:
        self.messages.append(("error", message))

    def log_warning(self, message: str) -> None:
        self.messages.append(("warning", message))


def response_content(response):
    return json.loads(response.body.decode("utf-8"))


@pytest.fixture
def fake_logger():
    return FakeLogger()
