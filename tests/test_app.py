import os
import tempfile

import pytest

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


@pytest.fixture
def app_with_db():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": db_path})
    with app.app_context():
        init_db()
    yield app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client_with_db(app_with_db):
    return app_with_db.test_client()


def test_patients_crud(client_with_db, app_with_db):
    response = client_with_db.get("/patients")
    assert response.status_code == 200
    assert b"Ava Morgan" in response.data

    response = client_with_db.post(
        "/patients/new",
        data={
            "first_name": "Sam",
            "last_name": "Taylor",
            "date_of_birth": "1995-02-20",
            "phone": "555-0199",
        },
        follow_redirects=True,
    )
    assert b"Sam Taylor" in response.data

    with app_with_db.app_context():
        patient = get_db().execute(
            "SELECT id FROM patients WHERE first_name = 'Sam'"
        ).fetchone()

    response = client_with_db.post(
        f"/patients/{patient['id']}/edit",
        data={
            "first_name": "Samantha",
            "last_name": "Taylor",
            "date_of_birth": "1995-02-20",
            "phone": "555-0199",
        },
        follow_redirects=True,
    )
    assert b"Samantha Taylor" in response.data

    response = client_with_db.post(f"/patients/{patient['id']}/delete", follow_redirects=True)
    assert b"Samantha Taylor" not in response.data


def test_doctors_crud(client_with_db, app_with_db):
    response = client_with_db.get("/doctors")
    assert response.status_code == 200
    assert b"Maya Patel" in response.data

    response = client_with_db.post(
        "/doctors/new",
        data={
            "first_name": "Noah",
            "last_name": "Chen",
            "specialty": "Pediatrics",
        },
        follow_redirects=True,
    )
    assert b"Noah Chen" in response.data

    with app_with_db.app_context():
        doctor = get_db().execute(
            "SELECT id FROM doctors WHERE first_name = 'Noah'"
        ).fetchone()

    response = client_with_db.post(
        f"/doctors/{doctor['id']}/edit",
        data={
            "first_name": "Noah",
            "last_name": "Chen",
            "specialty": "Internal Medicine",
        },
        follow_redirects=True,
    )
    assert b"Internal Medicine" in response.data

    response = client_with_db.post(f"/doctors/{doctor['id']}/delete", follow_redirects=True)
    assert b"Noah Chen" not in response.data


def test_appointments_crud(client_with_db, app_with_db):
    response = client_with_db.get("/appointments")
    assert response.status_code == 200
    assert b"Ava Morgan" in response.data
    assert b"Maya Patel" in response.data

    response = client_with_db.post(
        "/appointments/new",
        data={
            "patient_id": "1",
            "doctor_id": "2",
            "appointment_date": "2026-07-20",
            "appointment_time": "14:00",
            "reason": "Medication review",
            "status": "scheduled",
        },
        follow_redirects=True,
    )
    assert b"Medication review" in response.data

    with app_with_db.app_context():
        appointment = get_db().execute(
            "SELECT id FROM appointments WHERE reason = 'Medication review'"
        ).fetchone()

    response = client_with_db.post(
        f"/appointments/{appointment['id']}/edit",
        data={
            "patient_id": "1",
            "doctor_id": "2",
            "appointment_date": "2026-07-20",
            "appointment_time": "14:30",
            "reason": "Medication review",
            "status": "completed",
        },
        follow_redirects=True,
    )
    assert b"completed" in response.data

    response = client_with_db.post(
        f"/appointments/{appointment['id']}/delete",
        follow_redirects=True,
    )
    assert b"Medication review" not in response.data
