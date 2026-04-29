from app.routes.router import api_router


def test_api_router_includes_expected_routes():
    paths = {route.path for route in api_router.routes}

    assert "/api/v1/token" in paths
    assert "/api/v1/create" in paths
    assert "/api/v1/create-admin" in paths
