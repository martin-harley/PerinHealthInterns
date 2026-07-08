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
