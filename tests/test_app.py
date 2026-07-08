from app import create_app


def test_create_app_can_use_test_config():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})

    assert app.testing is True


def test_home_page_loads():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Perin Health Appointment Tracker" in response.data
