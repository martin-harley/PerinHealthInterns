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

    return app
