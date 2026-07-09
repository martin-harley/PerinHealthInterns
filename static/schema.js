const schemaNodes = document.querySelectorAll(".schema-node");
const schemaArrows = document.querySelectorAll(".schema-arrow");
const schemaTitle = document.querySelector("#schema-detail-title");
const schemaCopy = document.querySelector("#schema-detail-copy");
const schemaSql = document.querySelector("#schema-detail-sql");

const schemaDetails = {
  patients: {
    copy: "Patients are the people receiving care. Appointments point back to patients with patient_id.",
    sql: "JOIN patients ON appointments.patient_id = patients.id",
  },
  doctors: {
    copy: "Doctors are the clinicians assigned to appointments. Appointments point back to doctors with doctor_id.",
    sql: "JOIN doctors ON appointments.doctor_id = doctors.id",
  },
  appointments: {
    copy: "Appointments sit in the middle. Each appointment belongs to one patient and one doctor.",
    sql: "JOIN patients ON appointments.patient_id = patients.id\nJOIN doctors ON appointments.doctor_id = doctors.id",
  },
  appointment_notes: {
    copy: "Appointment notes belong to appointments. The appointment_id field links each note to one appointment.",
    sql: "JOIN appointment_notes ON appointment_notes.appointment_id = appointments.id",
  },
};

function selectSchemaTable(tableName) {
  schemaNodes.forEach((node) => {
    node.classList.toggle("is-active", node.dataset.table === tableName);
  });

  schemaArrows.forEach((arrow) => {
    const connectedTables = arrow.dataset.connects.split(" ");
    arrow.classList.toggle("is-active", connectedTables.includes(tableName));
  });

  if (schemaTitle && schemaCopy && schemaSql && schemaDetails[tableName]) {
    schemaTitle.textContent = tableName;
    schemaCopy.textContent = schemaDetails[tableName].copy;
    schemaSql.textContent = schemaDetails[tableName].sql;
  }
}

schemaNodes.forEach((node) => {
  node.addEventListener("click", () => selectSchemaTable(node.dataset.table));
});

selectSchemaTable("appointments");
