import os
import sqlite3

from flask import Flask, current_app, g, redirect, render_template, request, url_for


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

    def run_sandbox_sql(sql):
        cleaned_sql = sql.strip()
        if not cleaned_sql:
            return {
                "error": "Type or build a SQL statement before running it.",
                "sql": sql,
                "columns": [],
                "rows": [],
                "message": None,
            }

        db = get_db()
        try:
            cursor = db.execute(cleaned_sql)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = [dict(row) for row in cursor.fetchall()]
                return {
                    "error": None,
                    "sql": cleaned_sql,
                    "columns": columns,
                    "rows": rows,
                    "message": f"Query returned {len(rows)} row(s).",
                }

            db.commit()
            return {
                "error": None,
                "sql": cleaned_sql,
                "columns": [],
                "rows": [],
                "message": f"Query executed successfully. Rows changed: {cursor.rowcount}.",
            }
        except sqlite3.Error as error:
            db.rollback()
            return {
                "error": str(error),
                "sql": cleaned_sql,
                "columns": [],
                "rows": [],
                "message": None,
            }

    @app.route("/sandbox")
    def sandbox():
        return render_template("sandbox.html")

    @app.post("/sandbox/run")
    def sandbox_run():
        sql = request.form.get("sql", "")
        mode = request.form.get("mode", "typed")
        result = run_sandbox_sql(sql)
        return render_template("sandbox.html", result=result, active_mode=mode)

    @app.post("/sandbox/reset")
    def sandbox_reset():
        init_db()
        return render_template(
            "sandbox.html",
            reset_message="Sandbox reset to the seed training data.",
        )

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

    return app
