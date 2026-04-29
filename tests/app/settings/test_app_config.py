from app.settings import app_config
from app.settings.setting import AppEnvironmentSettings, Environment


class Settings:
    def __init__(self, environment):
        self.env = AppEnvironmentSettings(environment=environment)


def test_get_root_path_returns_empty_for_dev(monkeypatch):
    monkeypatch.setattr(app_config, "get_settings", lambda: Settings(Environment.DEV))

    assert app_config.AppConfig().get_root_path() == ""


def test_get_root_path_returns_prod_prefix(monkeypatch):
    monkeypatch.setattr(app_config, "get_settings", lambda: Settings(Environment.PROD))

    assert app_config.AppConfig().get_root_path() == "/crud/prod"
