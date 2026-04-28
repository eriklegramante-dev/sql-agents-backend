from app.settings import setting
from app.settings.setting import (
    AppEnvironmentSettings,
    DatabaseSettings,
    Environment,
    SecuritySettings,
    SentrySettings,
)


class Settings:
    def __init__(self, environment):
        self.env = AppEnvironmentSettings(environment=environment)


def test_database_settings_returns_dev_url(monkeypatch):
    monkeypatch.setattr(setting, "get_settings", lambda: Settings(Environment.DEV))
    database = DatabaseSettings(url_dev="dev-url", url_prod="prod-url")

    assert database.get_current_url() == "dev-url"


def test_database_settings_returns_prod_url(monkeypatch):
    monkeypatch.setattr(setting, "get_settings", lambda: Settings(Environment.PROD))
    database = DatabaseSettings(url_dev="dev-url", url_prod="prod-url")

    assert database.get_current_url() == "prod-url"


def test_database_settings_falls_back_to_dev_when_prod_url_empty(monkeypatch):
    monkeypatch.setattr(setting, "get_settings", lambda: Settings(Environment.PROD))
    database = DatabaseSettings(url_dev="dev-url", url_prod="")

    assert database.get_current_url() == "dev-url"


def test_settings_models_accept_values():
    assert AppEnvironmentSettings(environment="dev").environment == Environment.DEV
    assert SentrySettings(dns="").dns == ""
    assert SecuritySettings(
        secret_key="secret",
        jwt_algorithm="HS256",
        jwt_exp_minutes=60,
    ).jwt_exp_minutes == 60
