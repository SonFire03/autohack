from __future__ import annotations


def test_api_server_module_is_importable():
    import api.server as server

    assert hasattr(server, "app")
    assert server.app is None or server.app.title == "Autohack Local API"
