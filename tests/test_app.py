from app import create_app, get_db, init_db


def test_create_app_can_use_test_config():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})

    assert app.testing is True


def test_home_page_loads():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Perin Health Appointment Tracker" in response.data


def test_init_db_creates_required_tables():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})

    with app.app_context():
        init_db()
        rows = get_db().execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()

    table_names = [row["name"] for row in rows]
    assert table_names == [
        "appointment_notes",
        "appointments",
        "doctors",
        "patients",
    ]


def test_seed_data_adds_example_patient():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})

    with app.app_context():
        init_db()
        row = get_db().execute(
            "SELECT first_name, last_name FROM patients ORDER BY id LIMIT 1"
        ).fetchone()

    assert dict(row) == {"first_name": "Ava", "last_name": "Morgan"}
