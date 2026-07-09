import os
import tempfile
from pathlib import Path

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
    assert b"Sandbox" in response.data


def test_home_page_guides_beginner_workflow():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})
    client = app.test_client()

    response = client.get("/")

    assert b"Start with the app" in response.data
    assert b"Patients" in response.data
    assert b"Doctors" in response.data
    assert b"Appointments" in response.data
    assert b"Do not enter real patient information" in response.data


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


def test_appointment_detail_and_notes_crud(client_with_db, app_with_db):
    response = client_with_db.get("/appointments/1")
    assert response.status_code == 200
    assert b"Annual checkup" in response.data

    response = client_with_db.post(
        "/appointments/1/notes",
        data={"note_text": "Fictional note for teaching CRUD."},
        follow_redirects=True,
    )
    assert b"Fictional note for teaching CRUD." in response.data

    with app_with_db.app_context():
        note = get_db().execute(
            "SELECT id FROM appointment_notes WHERE note_text = 'Fictional note for teaching CRUD.'"
        ).fetchone()

    response = client_with_db.post(f"/notes/{note['id']}/delete", follow_redirects=True)
    assert b"Fictional note for teaching CRUD." not in response.data


def test_sandbox_page_has_builder_and_typed_tabs(client_with_db):
    response = client_with_db.get("/sandbox")

    assert response.status_code == 200
    assert b"SQL Sandbox" in response.data
    assert b"Drag & Build" in response.data
    assert b"Type SQL" in response.data
    assert b"draggable=\"true\"" in response.data
    assert b"SQL actions" in response.data
    assert b"Tables" in response.data
    assert b"Columns" in response.data
    assert b'data-sql="SELECT "' in response.data
    assert b'data-sql="patients"' in response.data
    assert b'data-sql="first_name"' in response.data
    assert b'id="builder-chip-board"' in response.data
    assert b'id="builder-sql-preview"' in response.data
    assert b'<pre class="built-sql-code"><code id="builder-sql-preview">' in response.data
    assert b'<input type="hidden" id="builder-sql" name="sql"' in response.data
    assert b'<textarea id="builder-sql"' not in response.data
    assert b"SELECT patients" not in response.data


def test_sandbox_typed_select_returns_rows(client_with_db):
    response = client_with_db.post(
        "/sandbox/run",
        data={"sql": "SELECT first_name, last_name FROM patients ORDER BY id;"},
    )

    assert response.status_code == 200
    assert b"Ava" in response.data
    assert b"Morgan" in response.data


def test_sandbox_result_appears_before_builder(client_with_db):
    response = client_with_db.post(
        "/sandbox/run",
        data={"sql": "SELECT first_name, last_name FROM patients ORDER BY id;"},
    )

    tips_index = response.data.index(b"Show SQL and tips")
    result_index = response.data.index(b"Result")
    builder_index = response.data.index(b"Drag & Build")
    assert tips_index < result_index < builder_index


def test_sandbox_builder_insert_executes_against_app_database(client_with_db, app_with_db):
    response = client_with_db.post(
        "/sandbox/run",
        data={
            "sql": "INSERT INTO patients (first_name, last_name, date_of_birth, phone) VALUES ('Riley', 'Sandbox', '1999-09-09', '555-0200');",
            "mode": "builder",
        },
    )

    assert response.status_code == 200
    assert b"Query executed successfully" in response.data
    with app_with_db.app_context():
        row = get_db().execute(
            "SELECT first_name, last_name FROM patients WHERE last_name = 'Sandbox'"
        ).fetchone()
    assert dict(row) == {"first_name": "Riley", "last_name": "Sandbox"}


def test_sandbox_reset_restores_seed_data(client_with_db, app_with_db):
    client_with_db.post(
        "/sandbox/run",
        data={
            "sql": "DELETE FROM patients WHERE first_name = 'Ava';",
            "mode": "typed",
        },
    )

    with app_with_db.app_context():
        missing = get_db().execute(
            "SELECT id FROM patients WHERE first_name = 'Ava'"
        ).fetchone()
    assert missing is None

    response = client_with_db.post("/sandbox/reset", follow_redirects=True)

    assert response.status_code == 200
    assert b"Sandbox reset to the seed training data" in response.data
    with app_with_db.app_context():
        restored = get_db().execute(
            "SELECT id FROM patients WHERE first_name = 'Ava'"
        ).fetchone()
    assert restored is not None


@pytest.mark.parametrize(
    ("path", "sql_terms"),
    [
        ("/", [b"Show SQL and tips", b"SELECT"]),
        ("/patients", [b"Show SQL and tips", b"SELECT", b"INSERT", b"UPDATE", b"DELETE"]),
        ("/patients/new", [b"Show SQL and tips", b"INSERT INTO patients"]),
        ("/patients/1/edit", [b"Show SQL and tips", b"UPDATE patients"]),
        ("/doctors", [b"Show SQL and tips", b"SELECT", b"INSERT", b"UPDATE", b"DELETE"]),
        ("/doctors/new", [b"Show SQL and tips", b"INSERT INTO doctors"]),
        ("/doctors/1/edit", [b"Show SQL and tips", b"UPDATE doctors"]),
        ("/appointments", [b"Show SQL and tips", b"JOIN patients", b"JOIN doctors"]),
        ("/appointments/new", [b"Show SQL and tips", b"INSERT INTO appointments"]),
        ("/appointments/1/edit", [b"Show SQL and tips", b"UPDATE appointments"]),
        ("/appointments/1", [b"Show SQL and tips", b"appointment_notes", b"INSERT INTO appointment_notes"]),
        ("/sandbox", [b"Show SQL and tips", b"SELECT", b"INSERT", b"UPDATE", b"DELETE"]),
    ],
)
def test_pages_show_sql_and_tips(client_with_db, path, sql_terms):
    response = client_with_db.get(path)

    assert response.status_code == 200
    for term in sql_terms:
        assert term in response.data


def test_readme_explains_learning_sequence():
    text = Path("README.md").read_text(encoding="utf-8")

    assert "Phase 1: Use the Web App" in text
    assert "Phase 5: Write SQL Directly" in text
    assert "fictional training data" in text


def test_exercises_cover_core_sql_operations():
    text = Path("exercises.sql").read_text(encoding="utf-8").upper()

    assert "SELECT" in text
    assert "INSERT" in text
    assert "UPDATE" in text
    assert "DELETE" in text
    assert "JOIN" in text
