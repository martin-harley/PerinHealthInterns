# Perin Health Appointment Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a beginner-friendly Flask and SQLite CRUD web app that teaches Perin Health interns relational database concepts through fictional patients, doctors, appointments, and appointment notes.

**Architecture:** Use one small Flask app with explicit SQL statements and simple Jinja templates. Keep the app intentionally direct so interns can trace a form submission to a SQL query and back to an HTML page. Use SQLite in a local `instance/appointment_tracker.sqlite` database, with tests creating temporary SQLite databases.

**Tech Stack:** Python, Flask, SQLite, pytest, HTML, CSS.

## Global Constraints

- All data in the project is fictional training data.
- The project is not intended for real patient information, production healthcare workflows, authentication, authorization, or HIPAA-related use.
- Use Python, Flask, SQLite, and HTML templates with simple forms.
- Use explicit SQL instead of an ORM.
- Required tables: `patients`, `doctors`, `appointments`, `appointment_notes`.
- Required appointment statuses: `scheduled`, `completed`, `cancelled`.
- Delete actions should use simple buttons with browser confirmation.
- Each list, form, and detail page should include a short "SQL concept" panel that names the SQL operation being taught.
- Do not include user accounts, login, permissions, billing, insurance, file uploads, appointment reminders, production deployment, advanced styling, or complex validation in the first version.

---

## File Structure

- `requirements.txt`: Flask and pytest dependencies.
- `app.py`: Flask app factory, SQLite helpers, CLI database initialization command, and all beginner-readable routes.
- `schema.sql`: Database schema with primary keys, foreign keys, and status constraint.
- `seed.sql`: Small fictional starter dataset.
- `templates/base.html`: Shared page shell and navigation.
- `templates/index.html`: Home page.
- `templates/patients_list.html`: Patient list and delete controls.
- `templates/patient_form.html`: Add/edit patient form.
- `templates/doctors_list.html`: Doctor list and delete controls.
- `templates/doctor_form.html`: Add/edit doctor form.
- `templates/appointments_list.html`: Appointment list with joined patient and doctor names.
- `templates/appointment_form.html`: Add/edit appointment form.
- `templates/appointment_detail.html`: Appointment detail page with notes.
- `static/styles.css`: Minimal readable styling.
- `tests/test_app.py`: Route, database, and CRUD tests using Flask's test client.
- `README.md`: Intern-facing setup and learning guide.
- `exercises.sql`: Direct SQL exercises for the transition after using the web app.

---

### Task 1: Project Setup and Flask Smoke Test

**Files:**
- Create: `requirements.txt`
- Create: `app.py`
- Create: `templates/base.html`
- Create: `templates/index.html`
- Create: `static/styles.css`
- Create: `tests/test_app.py`

**Interfaces:**
- Produces: `create_app(test_config: dict | None = None) -> flask.Flask`
- Produces: `GET /` returns a home page containing `Perin Health Appointment Tracker`

- [ ] **Step 1: Add dependencies**

Create `requirements.txt`:

```text
Flask>=3.1,<4
pytest>=8,<9
```

- [ ] **Step 2: Write the failing smoke tests**

Create `tests/test_app.py`:

```python
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
```

- [ ] **Step 3: Run the smoke tests and verify they fail**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: FAIL because `app.py` and `create_app` do not exist yet.

- [ ] **Step 4: Add the minimal Flask app factory**

Create `app.py`:

```python
import os

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "appointment_tracker.sqlite"),
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
```

Create `templates/base.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Perin Health Appointment Tracker{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
  </head>
  <body>
    <header>
      <h1>Perin Health Appointment Tracker</h1>
      <nav>
        <a href="{{ url_for('index') }}">Home</a>
      </nav>
    </header>
    <main>
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

Create `templates/index.html`:

```html
{% extends "base.html" %}

{% block content %}
  <section class="panel">
    <h2>Training Database</h2>
    <p>This app uses fictional training data to teach create, read, update, and delete operations.</p>
  </section>
{% endblock %}
```

Create `static/styles.css`:

```css
body {
  margin: 0;
  font-family: Arial, sans-serif;
  color: #1f2933;
  background: #f6f8fa;
}

header {
  background: #0f766e;
  color: white;
  padding: 1rem 1.5rem;
}

nav a {
  color: white;
  margin-right: 1rem;
}

main {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem;
}

.panel {
  background: white;
  border: 1px solid #d9e2ec;
  border-radius: 6px;
  padding: 1rem;
}
```

- [ ] **Step 5: Run the smoke tests and verify they pass**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt app.py templates/base.html templates/index.html static/styles.css tests/test_app.py
git commit -m "feat: add flask app shell"
```

---

### Task 2: SQLite Schema, Seed Data, and Database Helpers

**Files:**
- Modify: `app.py`
- Create: `schema.sql`
- Create: `seed.sql`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `create_app(test_config: dict | None = None) -> flask.Flask`
- Produces: `get_db() -> sqlite3.Connection`
- Produces: `init_db() -> None`
- Produces: Flask CLI command `flask --app app init-db`

- [ ] **Step 1: Add failing database tests**

Append to `tests/test_app.py`:

```python
from app import get_db, init_db


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
```

- [ ] **Step 2: Run database tests and verify they fail**

Run:

```bash
pytest tests/test_app.py::test_init_db_creates_required_tables tests/test_app.py::test_seed_data_adds_example_patient -v
```

Expected: FAIL because `get_db` and `init_db` are not implemented.

- [ ] **Step 3: Add schema**

Create `schema.sql`:

```sql
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS appointment_notes;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  date_of_birth TEXT NOT NULL,
  phone TEXT NOT NULL
);

CREATE TABLE doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  specialty TEXT NOT NULL
);

CREATE TABLE appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  doctor_id INTEGER NOT NULL,
  appointment_date TEXT NOT NULL,
  appointment_time TEXT NOT NULL,
  reason TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled')),
  FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
  FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE
);

CREATE TABLE appointment_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  appointment_id INTEGER NOT NULL,
  note_text TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (appointment_id) REFERENCES appointments (id) ON DELETE CASCADE
);
```

- [ ] **Step 4: Add fictional seed data**

Create `seed.sql`:

```sql
INSERT INTO patients (first_name, last_name, date_of_birth, phone)
VALUES
  ('Ava', 'Morgan', '1992-04-18', '555-0101'),
  ('Jordan', 'Lee', '1988-11-03', '555-0102');

INSERT INTO doctors (first_name, last_name, specialty)
VALUES
  ('Maya', 'Patel', 'Family Medicine'),
  ('Elena', 'Rivera', 'Cardiology');

INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
VALUES
  (1, 1, '2026-07-15', '09:00', 'Annual checkup', 'scheduled'),
  (2, 2, '2026-07-16', '10:30', 'Follow-up visit', 'completed');

INSERT INTO appointment_notes (appointment_id, note_text)
VALUES
  (2, 'Reviewed fictional follow-up plan.');
```

- [ ] **Step 5: Add database helpers and CLI command**

Modify `app.py`:

```python
import os
import sqlite3

from flask import Flask, current_app, g, render_template


def get_db():
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as schema_file:
        db.executescript(schema_file.read().decode("utf-8"))
    with current_app.open_resource("seed.sql") as seed_file:
        db.executescript(seed_file.read().decode("utf-8"))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "appointment_tracker.sqlite"),
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Initialized the database.")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
```

- [ ] **Step 6: Run tests and verify they pass**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: 4 passed.

- [ ] **Step 7: Commit**

```bash
git add app.py schema.sql seed.sql tests/test_app.py
git commit -m "feat: add sqlite schema and seed data"
```

---

### Task 3: Patients and Doctors CRUD

**Files:**
- Modify: `app.py`
- Modify: `templates/base.html`
- Create: `templates/patients_list.html`
- Create: `templates/patient_form.html`
- Create: `templates/doctors_list.html`
- Create: `templates/doctor_form.html`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `get_db() -> sqlite3.Connection`
- Produces: patient routes `GET /patients`, `GET|POST /patients/new`, `GET|POST /patients/<id>/edit`, `POST /patients/<id>/delete`
- Produces: doctor routes `GET /doctors`, `GET|POST /doctors/new`, `GET|POST /doctors/<id>/edit`, `POST /doctors/<id>/delete`

- [ ] **Step 1: Add failing CRUD route tests**

Append to `tests/test_app.py`:

```python
import os
import tempfile

import pytest


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
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run:

```bash
pytest tests/test_app.py::test_patients_crud tests/test_app.py::test_doctors_crud -v
```

Expected: FAIL with 404 responses because the CRUD routes do not exist.

- [ ] **Step 3: Add patient and doctor routes**

Modify `app.py` imports:

```python
from flask import Flask, current_app, g, redirect, render_template, request, url_for
```

Add these route functions inside `create_app` before `return app`:

```python
    @app.route("/patients")
    def patients_list():
        patients = get_db().execute(
            "SELECT id, first_name, last_name, date_of_birth, phone FROM patients ORDER BY last_name, first_name"
        ).fetchall()
        return render_template("patients_list.html", patients=patients)

    @app.route("/patients/new", methods=("GET", "POST"))
    def patient_new():
        if request.method == "POST":
            get_db().execute(
                "INSERT INTO patients (first_name, last_name, date_of_birth, phone) VALUES (?, ?, ?, ?)",
                (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["date_of_birth"],
                    request.form["phone"],
                ),
            )
            get_db().commit()
            return redirect(url_for("patients_list"))
        return render_template("patient_form.html", patient=None)

    @app.route("/patients/<int:patient_id>/edit", methods=("GET", "POST"))
    def patient_edit(patient_id):
        patient = get_db().execute(
            "SELECT id, first_name, last_name, date_of_birth, phone FROM patients WHERE id = ?",
            (patient_id,),
        ).fetchone()
        if request.method == "POST":
            get_db().execute(
                "UPDATE patients SET first_name = ?, last_name = ?, date_of_birth = ?, phone = ? WHERE id = ?",
                (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["date_of_birth"],
                    request.form["phone"],
                    patient_id,
                ),
            )
            get_db().commit()
            return redirect(url_for("patients_list"))
        return render_template("patient_form.html", patient=patient)

    @app.post("/patients/<int:patient_id>/delete")
    def patient_delete(patient_id):
        get_db().execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        get_db().commit()
        return redirect(url_for("patients_list"))

    @app.route("/doctors")
    def doctors_list():
        doctors = get_db().execute(
            "SELECT id, first_name, last_name, specialty FROM doctors ORDER BY last_name, first_name"
        ).fetchall()
        return render_template("doctors_list.html", doctors=doctors)

    @app.route("/doctors/new", methods=("GET", "POST"))
    def doctor_new():
        if request.method == "POST":
            get_db().execute(
                "INSERT INTO doctors (first_name, last_name, specialty) VALUES (?, ?, ?)",
                (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["specialty"],
                ),
            )
            get_db().commit()
            return redirect(url_for("doctors_list"))
        return render_template("doctor_form.html", doctor=None)

    @app.route("/doctors/<int:doctor_id>/edit", methods=("GET", "POST"))
    def doctor_edit(doctor_id):
        doctor = get_db().execute(
            "SELECT id, first_name, last_name, specialty FROM doctors WHERE id = ?",
            (doctor_id,),
        ).fetchone()
        if request.method == "POST":
            get_db().execute(
                "UPDATE doctors SET first_name = ?, last_name = ?, specialty = ? WHERE id = ?",
                (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["specialty"],
                    doctor_id,
                ),
            )
            get_db().commit()
            return redirect(url_for("doctors_list"))
        return render_template("doctor_form.html", doctor=doctor)

    @app.post("/doctors/<int:doctor_id>/delete")
    def doctor_delete(doctor_id):
        get_db().execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        get_db().commit()
        return redirect(url_for("doctors_list"))
```

- [ ] **Step 4: Add navigation and templates**

Update the `nav` in `templates/base.html`:

```html
      <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('patients_list') }}">Patients</a>
        <a href="{{ url_for('doctors_list') }}">Doctors</a>
      </nav>
```

Create `templates/patients_list.html`:

```html
{% extends "base.html" %}

{% block title %}Patients{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: SELECT reads rows from the patients table.</section>
  <p><a class="button" href="{{ url_for('patient_new') }}">Add patient</a></p>
  <table>
    <tr><th>Name</th><th>Date of birth</th><th>Phone</th><th>Actions</th></tr>
    {% for patient in patients %}
      <tr>
        <td>{{ patient.first_name }} {{ patient.last_name }}</td>
        <td>{{ patient.date_of_birth }}</td>
        <td>{{ patient.phone }}</td>
        <td>
          <a href="{{ url_for('patient_edit', patient_id=patient.id) }}">Edit</a>
          <form class="inline" method="post" action="{{ url_for('patient_delete', patient_id=patient.id) }}" onsubmit="return confirm('Delete this patient?');">
            <button type="submit">Delete</button>
          </form>
        </td>
      </tr>
    {% endfor %}
  </table>
{% endblock %}
```

Create `templates/patient_form.html`:

```html
{% extends "base.html" %}

{% block title %}{% if patient %}Edit patient{% else %}Add patient{% endif %}{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: {% if patient %}UPDATE changes an existing patient row.{% else %}INSERT creates a new patient row.{% endif %}</section>
  <form method="post">
    <label>First name <input name="first_name" value="{{ patient.first_name if patient else '' }}" required></label>
    <label>Last name <input name="last_name" value="{{ patient.last_name if patient else '' }}" required></label>
    <label>Date of birth <input type="date" name="date_of_birth" value="{{ patient.date_of_birth if patient else '' }}" required></label>
    <label>Phone <input name="phone" value="{{ patient.phone if patient else '' }}" required></label>
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

Create `templates/doctors_list.html`:

```html
{% extends "base.html" %}

{% block title %}Doctors{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: SELECT reads rows from the doctors table.</section>
  <p><a class="button" href="{{ url_for('doctor_new') }}">Add doctor</a></p>
  <table>
    <tr><th>Name</th><th>Specialty</th><th>Actions</th></tr>
    {% for doctor in doctors %}
      <tr>
        <td>{{ doctor.first_name }} {{ doctor.last_name }}</td>
        <td>{{ doctor.specialty }}</td>
        <td>
          <a href="{{ url_for('doctor_edit', doctor_id=doctor.id) }}">Edit</a>
          <form class="inline" method="post" action="{{ url_for('doctor_delete', doctor_id=doctor.id) }}" onsubmit="return confirm('Delete this doctor?');">
            <button type="submit">Delete</button>
          </form>
        </td>
      </tr>
    {% endfor %}
  </table>
{% endblock %}
```

Create `templates/doctor_form.html`:

```html
{% extends "base.html" %}

{% block title %}{% if doctor %}Edit doctor{% else %}Add doctor{% endif %}{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: {% if doctor %}UPDATE changes an existing doctor row.{% else %}INSERT creates a new doctor row.{% endif %}</section>
  <form method="post">
    <label>First name <input name="first_name" value="{{ doctor.first_name if doctor else '' }}" required></label>
    <label>Last name <input name="last_name" value="{{ doctor.last_name if doctor else '' }}" required></label>
    <label>Specialty <input name="specialty" value="{{ doctor.specialty if doctor else '' }}" required></label>
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

- [ ] **Step 5: Add table and form styles**

Append to `static/styles.css`:

```css
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

th,
td {
  border: 1px solid #d9e2ec;
  padding: 0.6rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.8rem;
}

input,
select,
textarea {
  display: block;
  width: 100%;
  max-width: 420px;
  padding: 0.5rem;
  margin-top: 0.25rem;
}

button,
.button {
  background: #0f766e;
  border: 0;
  color: white;
  display: inline-block;
  padding: 0.5rem 0.75rem;
  text-decoration: none;
}

.inline {
  display: inline;
}

.sql-panel {
  background: #eef6ff;
  border-left: 4px solid #2563eb;
  margin-bottom: 1rem;
  padding: 0.75rem;
}
```

- [ ] **Step 6: Run tests and verify they pass**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add app.py templates/base.html templates/patients_list.html templates/patient_form.html templates/doctors_list.html templates/doctor_form.html static/styles.css tests/test_app.py
git commit -m "feat: add patient and doctor crud"
```

---

### Task 4: Appointments CRUD with Patient and Doctor Relationships

**Files:**
- Modify: `app.py`
- Modify: `templates/base.html`
- Create: `templates/appointments_list.html`
- Create: `templates/appointment_form.html`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `patients.id`, `doctors.id`
- Produces: appointment routes `GET /appointments`, `GET|POST /appointments/new`, `GET|POST /appointments/<id>/edit`, `POST /appointments/<id>/delete`
- Produces: appointment list query joined to patient and doctor names

- [ ] **Step 1: Add failing appointment CRUD test**

Append to `tests/test_app.py`:

```python
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
```

- [ ] **Step 2: Run appointment test and verify it fails**

Run:

```bash
pytest tests/test_app.py::test_appointments_crud -v
```

Expected: FAIL with 404 because appointment routes do not exist.

- [ ] **Step 3: Add appointment routes**

Add inside `create_app` before `return app`:

```python
    def load_people_for_appointment_form():
        patients = get_db().execute(
            "SELECT id, first_name, last_name FROM patients ORDER BY last_name, first_name"
        ).fetchall()
        doctors = get_db().execute(
            "SELECT id, first_name, last_name FROM doctors ORDER BY last_name, first_name"
        ).fetchall()
        return patients, doctors

    @app.route("/appointments")
    def appointments_list():
        appointments = get_db().execute(
            """
            SELECT
              appointments.id,
              appointments.appointment_date,
              appointments.appointment_time,
              appointments.reason,
              appointments.status,
              patients.first_name || ' ' || patients.last_name AS patient_name,
              doctors.first_name || ' ' || doctors.last_name AS doctor_name
            FROM appointments
            JOIN patients ON appointments.patient_id = patients.id
            JOIN doctors ON appointments.doctor_id = doctors.id
            ORDER BY appointments.appointment_date, appointments.appointment_time
            """
        ).fetchall()
        return render_template("appointments_list.html", appointments=appointments)

    @app.route("/appointments/new", methods=("GET", "POST"))
    def appointment_new():
        patients, doctors = load_people_for_appointment_form()
        if request.method == "POST":
            get_db().execute(
                """
                INSERT INTO appointments
                  (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    request.form["patient_id"],
                    request.form["doctor_id"],
                    request.form["appointment_date"],
                    request.form["appointment_time"],
                    request.form["reason"],
                    request.form["status"],
                ),
            )
            get_db().commit()
            return redirect(url_for("appointments_list"))
        return render_template(
            "appointment_form.html",
            appointment=None,
            patients=patients,
            doctors=doctors,
            statuses=("scheduled", "completed", "cancelled"),
        )

    @app.route("/appointments/<int:appointment_id>/edit", methods=("GET", "POST"))
    def appointment_edit(appointment_id):
        appointment = get_db().execute(
            "SELECT id, patient_id, doctor_id, appointment_date, appointment_time, reason, status FROM appointments WHERE id = ?",
            (appointment_id,),
        ).fetchone()
        patients, doctors = load_people_for_appointment_form()
        if request.method == "POST":
            get_db().execute(
                """
                UPDATE appointments
                SET patient_id = ?, doctor_id = ?, appointment_date = ?, appointment_time = ?, reason = ?, status = ?
                WHERE id = ?
                """,
                (
                    request.form["patient_id"],
                    request.form["doctor_id"],
                    request.form["appointment_date"],
                    request.form["appointment_time"],
                    request.form["reason"],
                    request.form["status"],
                    appointment_id,
                ),
            )
            get_db().commit()
            return redirect(url_for("appointments_list"))
        return render_template(
            "appointment_form.html",
            appointment=appointment,
            patients=patients,
            doctors=doctors,
            statuses=("scheduled", "completed", "cancelled"),
        )

    @app.post("/appointments/<int:appointment_id>/delete")
    def appointment_delete(appointment_id):
        get_db().execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        get_db().commit()
        return redirect(url_for("appointments_list"))
```

- [ ] **Step 4: Add navigation and templates**

Update the `nav` in `templates/base.html`:

```html
      <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('patients_list') }}">Patients</a>
        <a href="{{ url_for('doctors_list') }}">Doctors</a>
        <a href="{{ url_for('appointments_list') }}">Appointments</a>
      </nav>
```

Create `templates/appointments_list.html`:

```html
{% extends "base.html" %}

{% block title %}Appointments{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: SELECT with JOIN reads appointments with patient and doctor names.</section>
  <p><a class="button" href="{{ url_for('appointment_new') }}">Add appointment</a></p>
  <table>
    <tr><th>Date</th><th>Time</th><th>Patient</th><th>Doctor</th><th>Reason</th><th>Status</th><th>Actions</th></tr>
    {% for appointment in appointments %}
      <tr>
        <td>{{ appointment.appointment_date }}</td>
        <td>{{ appointment.appointment_time }}</td>
        <td>{{ appointment.patient_name }}</td>
        <td>{{ appointment.doctor_name }}</td>
        <td>{{ appointment.reason }}</td>
        <td>{{ appointment.status }}</td>
        <td>
          <a href="{{ url_for('appointment_edit', appointment_id=appointment.id) }}">Edit</a>
          <form class="inline" method="post" action="{{ url_for('appointment_delete', appointment_id=appointment.id) }}" onsubmit="return confirm('Delete this appointment?');">
            <button type="submit">Delete</button>
          </form>
        </td>
      </tr>
    {% endfor %}
  </table>
{% endblock %}
```

Create `templates/appointment_form.html`:

```html
{% extends "base.html" %}

{% block title %}{% if appointment %}Edit appointment{% else %}Add appointment{% endif %}{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: {% if appointment %}UPDATE changes an existing appointment row.{% else %}INSERT creates a new appointment row with patient_id and doctor_id foreign keys.{% endif %}</section>
  <form method="post">
    <label>Patient
      <select name="patient_id" required>
        {% for patient in patients %}
          <option value="{{ patient.id }}" {% if appointment and appointment.patient_id == patient.id %}selected{% endif %}>{{ patient.first_name }} {{ patient.last_name }}</option>
        {% endfor %}
      </select>
    </label>
    <label>Doctor
      <select name="doctor_id" required>
        {% for doctor in doctors %}
          <option value="{{ doctor.id }}" {% if appointment and appointment.doctor_id == doctor.id %}selected{% endif %}>{{ doctor.first_name }} {{ doctor.last_name }}</option>
        {% endfor %}
      </select>
    </label>
    <label>Date <input type="date" name="appointment_date" value="{{ appointment.appointment_date if appointment else '' }}" required></label>
    <label>Time <input type="time" name="appointment_time" value="{{ appointment.appointment_time if appointment else '' }}" required></label>
    <label>Reason <input name="reason" value="{{ appointment.reason if appointment else '' }}" required></label>
    <label>Status
      <select name="status" required>
        {% for status in statuses %}
          <option value="{{ status }}" {% if appointment and appointment.status == status %}selected{% endif %}>{{ status }}</option>
        {% endfor %}
      </select>
    </label>
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

- [ ] **Step 5: Run tests and verify they pass**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add app.py templates/base.html templates/appointments_list.html templates/appointment_form.html tests/test_app.py
git commit -m "feat: add appointment crud"
```

---

### Task 5: Appointment Detail Page and Notes CRUD

**Files:**
- Modify: `app.py`
- Modify: `templates/appointments_list.html`
- Create: `templates/appointment_detail.html`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `appointments.id`
- Produces: `GET /appointments/<id>`
- Produces: `POST /appointments/<id>/notes`
- Produces: `POST /notes/<id>/delete`

- [ ] **Step 1: Add failing notes tests**

Append to `tests/test_app.py`:

```python
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
```

- [ ] **Step 2: Run notes test and verify it fails**

Run:

```bash
pytest tests/test_app.py::test_appointment_detail_and_notes_crud -v
```

Expected: FAIL with 404 because detail and note routes do not exist.

- [ ] **Step 3: Add appointment detail and note routes**

Add inside `create_app` before `return app`:

```python
    @app.route("/appointments/<int:appointment_id>")
    def appointment_detail(appointment_id):
        appointment = get_db().execute(
            """
            SELECT
              appointments.id,
              appointments.appointment_date,
              appointments.appointment_time,
              appointments.reason,
              appointments.status,
              patients.first_name || ' ' || patients.last_name AS patient_name,
              doctors.first_name || ' ' || doctors.last_name AS doctor_name
            FROM appointments
            JOIN patients ON appointments.patient_id = patients.id
            JOIN doctors ON appointments.doctor_id = doctors.id
            WHERE appointments.id = ?
            """,
            (appointment_id,),
        ).fetchone()
        notes = get_db().execute(
            "SELECT id, note_text, created_at FROM appointment_notes WHERE appointment_id = ? ORDER BY created_at DESC, id DESC",
            (appointment_id,),
        ).fetchall()
        return render_template("appointment_detail.html", appointment=appointment, notes=notes)

    @app.post("/appointments/<int:appointment_id>/notes")
    def note_new(appointment_id):
        get_db().execute(
            "INSERT INTO appointment_notes (appointment_id, note_text) VALUES (?, ?)",
            (appointment_id, request.form["note_text"]),
        )
        get_db().commit()
        return redirect(url_for("appointment_detail", appointment_id=appointment_id))

    @app.post("/notes/<int:note_id>/delete")
    def note_delete(note_id):
        row = get_db().execute(
            "SELECT appointment_id FROM appointment_notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        appointment_id = row["appointment_id"]
        get_db().execute("DELETE FROM appointment_notes WHERE id = ?", (note_id,))
        get_db().commit()
        return redirect(url_for("appointment_detail", appointment_id=appointment_id))
```

- [ ] **Step 4: Link appointment list to detail pages**

Modify the reason cell in `templates/appointments_list.html`:

```html
        <td><a href="{{ url_for('appointment_detail', appointment_id=appointment.id) }}">{{ appointment.reason }}</a></td>
```

- [ ] **Step 5: Add appointment detail template**

Create `templates/appointment_detail.html`:

```html
{% extends "base.html" %}

{% block title %}Appointment detail{% endblock %}

{% block content %}
  <section class="sql-panel">SQL concept: SELECT with JOIN reads one appointment and its related patient, doctor, and notes.</section>

  <section class="panel">
    <h2>{{ appointment.reason }}</h2>
    <p><strong>Patient:</strong> {{ appointment.patient_name }}</p>
    <p><strong>Doctor:</strong> {{ appointment.doctor_name }}</p>
    <p><strong>Date:</strong> {{ appointment.appointment_date }} at {{ appointment.appointment_time }}</p>
    <p><strong>Status:</strong> {{ appointment.status }}</p>
  </section>

  <section class="panel">
    <h2>Notes</h2>
    <section class="sql-panel">SQL concept: INSERT creates a note connected by appointment_id.</section>
    <form method="post" action="{{ url_for('note_new', appointment_id=appointment.id) }}">
      <label>New note
        <textarea name="note_text" rows="4" required></textarea>
      </label>
      <button type="submit">Add note</button>
    </form>

    {% for note in notes %}
      <article class="note">
        <p>{{ note.note_text }}</p>
        <small>{{ note.created_at }}</small>
        <form method="post" action="{{ url_for('note_delete', note_id=note.id) }}" onsubmit="return confirm('Delete this note?');">
          <button type="submit">Delete note</button>
        </form>
      </article>
    {% else %}
      <p>No notes yet.</p>
    {% endfor %}
  </section>
{% endblock %}
```

- [ ] **Step 6: Add note styling**

Append to `static/styles.css`:

```css
.note {
  border-top: 1px solid #d9e2ec;
  margin-top: 1rem;
  padding-top: 1rem;
}
```

- [ ] **Step 7: Run tests and verify they pass**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add app.py templates/appointments_list.html templates/appointment_detail.html static/styles.css tests/test_app.py
git commit -m "feat: add appointment notes"
```

---

### Task 6: Intern Learning Guide and Direct SQL Exercises

**Files:**
- Create: `README.md`
- Create: `exercises.sql`
- Modify: `templates/index.html`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: app routes from Tasks 1-5
- Produces: intern setup instructions
- Produces: direct SQL exercises covering `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and `JOIN`

- [ ] **Step 1: Add failing content tests**

Append to `tests/test_app.py`:

```python
from pathlib import Path


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
```

- [ ] **Step 2: Run content tests and verify they fail**

Run:

```bash
pytest tests/test_app.py::test_readme_explains_learning_sequence tests/test_app.py::test_exercises_cover_core_sql_operations -v
```

Expected: FAIL because `README.md` and `exercises.sql` do not exist.

- [ ] **Step 3: Add intern-facing README**

Create `README.md`:

````markdown
# Perin Health Appointment Tracker

This is a beginner CRUD database project for Perin Health interns. It uses fictional training data only.

Do not enter real patient information into this app.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Open the local URL printed by Flask.

## Phase 1: Use the Web App

Use the Patients, Doctors, Appointments, and Notes pages. Add, view, edit, and delete records.

## Phase 2: Understand Tables

The database has four tables:

- `patients`
- `doctors`
- `appointments`
- `appointment_notes`

Each row has an `id`. Other tables use those IDs to connect related records.

## Phase 3: Map Buttons to CRUD

- Add forms teach `INSERT`.
- List pages teach `SELECT`.
- Edit forms teach `UPDATE`.
- Delete buttons teach `DELETE`.

## Phase 4: Learn Relationships

Appointments connect patients and doctors:

- `appointments.patient_id` points to `patients.id`
- `appointments.doctor_id` points to `doctors.id`
- `appointment_notes.appointment_id` points to `appointments.id`

## Phase 5: Write SQL Directly

After using the app, open `exercises.sql` and run the queries against the SQLite database.
````

- [ ] **Step 4: Add SQL exercises**

Create `exercises.sql`:

```sql
-- Perin Health Appointment Tracker SQL exercises
-- Use fictional training data only.

-- 1. SELECT: Show all patients.
SELECT id, first_name, last_name, date_of_birth, phone
FROM patients;

-- 2. SELECT: Show scheduled appointments.
SELECT id, appointment_date, appointment_time, reason, status
FROM appointments
WHERE status = 'scheduled';

-- 3. INSERT: Add a fictional patient.
INSERT INTO patients (first_name, last_name, date_of_birth, phone)
VALUES ('Chris', 'Example', '1990-01-01', '555-0103');

-- 4. UPDATE: Mark one appointment completed.
UPDATE appointments
SET status = 'completed'
WHERE id = 1;

-- 5. DELETE: Remove one incorrect note.
DELETE FROM appointment_notes
WHERE id = 1;

-- 6. JOIN: Show appointments with patient and doctor names.
SELECT
  appointments.id,
  appointments.appointment_date,
  appointments.appointment_time,
  patients.first_name || ' ' || patients.last_name AS patient_name,
  doctors.first_name || ' ' || doctors.last_name AS doctor_name,
  appointments.reason,
  appointments.status
FROM appointments
JOIN patients ON appointments.patient_id = patients.id
JOIN doctors ON appointments.doctor_id = doctors.id;
```

- [ ] **Step 5: Link learning guide from home page**

Modify `templates/index.html`:

```html
{% extends "base.html" %}

{% block content %}
  <section class="panel">
    <h2>Training Database</h2>
    <p>This app uses fictional training data to teach create, read, update, and delete operations.</p>
    <p>Start by using the web app, then open the README and exercises.sql files to learn the SQL underneath.</p>
  </section>
{% endblock %}
```

- [ ] **Step 6: Run all tests and verify they pass**

Run:

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add README.md exercises.sql templates/index.html tests/test_app.py
git commit -m "docs: add intern learning guide"
```

---

### Task 7: Final Verification and Manual Run

**Files:**
- Modify only if verification reveals a defect in files from earlier tasks.

**Interfaces:**
- Consumes: all app routes and documentation
- Produces: a verified local Flask app ready for the user to try

- [ ] **Step 1: Run the complete test suite**

Run:

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Initialize the development database**

Run:

```bash
flask --app app init-db
```

Expected output:

```text
Initialized the database.
```

- [ ] **Step 3: Start the local server**

Run:

```bash
flask --app app run --debug
```

Expected: Flask prints a local URL, usually `http://127.0.0.1:5000`.

- [ ] **Step 4: Manually verify core screens**

Open the local URL and verify:

- Home page loads.
- Patients page lists Ava Morgan.
- Doctors page lists Maya Patel.
- Appointments page lists appointment rows with patient and doctor names.
- Appointment detail page shows notes.
- Each page has a visible SQL concept panel.

- [ ] **Step 5: Stop the server**

Stop Flask with `Ctrl+C`.

- [ ] **Step 6: Confirm git status**

Run:

```bash
git status --short
```

Expected: no output.

If manual verification required fixes, commit those fixes:

```bash
git add app.py templates static tests README.md exercises.sql schema.sql seed.sql
git commit -m "fix: complete appointment tracker verification"
```

If no fixes were required, no commit is needed.
