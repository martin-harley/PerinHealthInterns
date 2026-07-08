# Perin Health Appointment Tracker Design

## Purpose

Create a simple CRUD database project for Perin Health interns with little to no software experience. The project should teach relational database basics through a small web app first, then gradually transition interns into writing SQL directly.

All data in the project is fictional training data. The project is not intended for real patient information, production healthcare workflows, authentication, authorization, or HIPAA-related use.

## Recommended Stack

- Python
- Flask
- SQLite
- HTML templates with simple forms

This stack keeps setup and code small enough for beginners to understand. SQLite also keeps the database visible as a single local file, which makes it easier to connect the web app to the underlying data.

## Core Concept

The app will be called **Perin Health Appointment Tracker**.

Interns will use a simple web interface to manage:

- Patients
- Doctors
- Appointments
- Appointment notes

Each screen will map to common database operations:

- Create records with `INSERT`
- Read records with `SELECT`
- Update records with `UPDATE`
- Delete records with `DELETE`
- Connect related data with `JOIN`

## Data Model

### `patients`

Stores fictional patient records.

Required fields:

- `id`
- `first_name`
- `last_name`
- `date_of_birth`
- `phone`

### `doctors`

Stores fictional doctor records.

Required fields:

- `id`
- `first_name`
- `last_name`
- `specialty`

### `appointments`

Stores scheduled appointments. Each appointment belongs to one patient and one doctor.

Required fields:

- `id`
- `patient_id`
- `doctor_id`
- `appointment_date`
- `appointment_time`
- `reason`
- `status`

Required appointment statuses:

- `scheduled`
- `completed`
- `cancelled`

### `appointment_notes`

Stores notes attached to appointments. Each note belongs to one appointment.

Required fields:

- `id`
- `appointment_id`
- `note_text`
- `created_at`

## Relationships

- One patient can have many appointments.
- One doctor can have many appointments.
- One appointment belongs to one patient.
- One appointment belongs to one doctor.
- One appointment can have many notes.
- One note belongs to one appointment.

These relationships are the main teaching tool for explaining primary keys, foreign keys, and joins.

## Web Interface

The first version should include these screens:

- Home page with links to each section
- Patients list
- Add patient form
- Edit patient form
- Doctors list
- Add doctor form
- Edit doctor form
- Appointments list
- Add appointment form
- Edit appointment form
- Appointment detail page
- Add appointment note form

Delete actions should use simple buttons with browser confirmation.

## SQL Learning Support

The app should gradually reveal the SQL underneath the interface. Each list, form, and detail page should include a short "SQL concept" panel that names the SQL operation being taught.

Examples:

- Adding a patient teaches `INSERT`.
- Viewing appointments teaches `SELECT`.
- Editing an appointment status teaches `UPDATE`.
- Deleting an incorrect note teaches `DELETE`.
- Viewing appointments with patient and doctor names teaches `JOIN`.

The exact SQL does not need to be shown everywhere at first. Early lessons can describe the operation conceptually, then later lessons can show and run the real SQL.

## Learning Sequence

### Phase 1: Use the App

Interns use the web interface without editing code. They should understand what the app does and how records are added, viewed, changed, and deleted.

### Phase 2: Understand Tables

Interns learn what each table stores and inspect sample data in SQLite.

They should be able to answer:

- What is a row?
- What is a column?
- Why does each table have an `id`?
- Which table stores patients?
- Which table stores doctors?
- Which table connects patients and doctors?

### Phase 3: Map Buttons to CRUD

Interns connect each app action to a SQL operation.

Examples:

- Submit "Add Patient" form -> create -> `INSERT`
- Open patients page -> read -> `SELECT`
- Change appointment status -> update -> `UPDATE`
- Remove mistaken note -> delete -> `DELETE`

### Phase 4: Learn Relationships

Interns learn that `appointments.patient_id` points to `patients.id`, and `appointments.doctor_id` points to `doctors.id`.

They also learn that `appointment_notes.appointment_id` points to `appointments.id`.

### Phase 5: Write SQL Directly

Interns move from using the app to running SQL queries directly.

Starter exercises:

- Select all patients.
- Select all doctors.
- Select all scheduled appointments.
- Insert a new fictional patient.
- Update an appointment status to `completed`.
- Delete an incorrect note.
- Join appointments with patient and doctor names.

## Success Criteria

The project is successful when interns can:

- Explain what each table stores.
- Explain why tables use IDs.
- Use the web app to create, read, update, and delete records.
- Identify which SQL operation is behind each app action.
- Explain the relationship between patients, doctors, appointments, and notes.
- Write basic `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statements.
- Write a simple `JOIN` that shows appointments with patient and doctor names.

## Out of Scope

The first version will not include:

- Real patient data
- User accounts
- Login or password management
- Role-based permissions
- Billing
- Insurance
- File uploads
- Appointment reminders
- Production deployment
- Advanced styling
- Complex validation

These exclusions keep the project focused on relational databases and CRUD.

## Implementation Notes

The code should be intentionally simple and readable. It should avoid unnecessary abstractions so interns can trace a request from a form submission to a SQL statement and back to an HTML page.

The project should prefer explicit SQL over an ORM for the first version. This makes the connection between the web interface and relational database concepts easier to see.
