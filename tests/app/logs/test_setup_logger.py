import logging

from app.logs import setup_logger
from app.logs.setup_logger import LoggerManager


class Settings:
    class Sentry:
        dns = ""

    sentry = Sentry()


def test_logger_manager_logs_with_debug_enabled(monkeypatch):
    monkeypatch.setattr(setup_logger, "get_trace_id", lambda: "trace-1")
    manager = LoggerManager(debug=True, settings=Settings())

    manager.log_info("info")
    manager.log_debug("debug")
    manager.log_error("error")
    manager.log_warning("warning")

    assert manager.logger.level == logging.DEBUG


def test_logger_manager_initializes_sentry_when_not_debug(monkeypatch):
    calls = {}

    monkeypatch.setattr(setup_logger, "get_trace_id", lambda: None)
    monkeypatch.setattr(
        setup_logger.sentry_sdk,
        "init",
        lambda **kwargs: calls.setdefault("init", kwargs),
    )
    monkeypatch.setattr(
        setup_logger.sentry_sdk,
        "capture_message",
        lambda *args, **kwargs: calls.setdefault("capture", args),
    )

    manager = LoggerManager(debug=False, settings=Settings())
    manager.log_error("error")
    manager.log_warning("warning")

    assert "init" in calls
    assert manager.logger.level == logging.INFO
