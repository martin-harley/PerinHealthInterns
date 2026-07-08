# Perin Health Appointment Tracker

This is a beginner CRUD database project for Perin Health interns. It uses fictional training data only.

Do not enter real patient information into this app.

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app init-db
python -m flask --app app run
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

## SQL Sandbox

Use the Sandbox tab to practice SQL inside the web app. The drag builder helps assemble starter statements, and the typed editor lets you write SQL directly.

Sandbox queries run against the same fictional SQLite database used by the app. Use **Reset training database** to restore the original seed data after experiments.
