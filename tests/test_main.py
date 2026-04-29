from main import app


def test_app_metadata_and_routes():
    paths = {route.path for route in app.routes}

    assert app.title == "User Management API"
    assert "/api/v1/token" in paths
    assert "/api/v1/create" in paths
    assert "/openapi.json" in paths
