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
