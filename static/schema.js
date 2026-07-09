const schemaNodes = document.querySelectorAll(".schema-node");
const schemaArrows = document.querySelectorAll(".schema-arrow");
const schemaMap = document.querySelector(".schema-map");
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

function getPortCenter(fieldName, portSelector) {
  const field = document.querySelector(`[data-field="${fieldName}"]`);
  const port = field?.querySelector(portSelector);
  if (!schemaMap || !port) return null;
  const mapBox = schemaMap.getBoundingClientRect();
  const portBox = port.getBoundingClientRect();
  return {
    x: portBox.left + portBox.width / 2 - mapBox.left,
    y: portBox.top + portBox.height / 2 - mapBox.top,
  };
}

function drawSchemaArrows() {
  if (!schemaMap) return;
  const mapBox = schemaMap.getBoundingClientRect();
  const svg = schemaMap.querySelector(".schema-arrows");
  svg.setAttribute("viewBox", `0 0 ${mapBox.width} ${mapBox.height}`);

  schemaArrows.forEach((arrow) => {
    const start = getPortCenter(arrow.dataset.from, ".schema-port-out");
    const end = getPortCenter(arrow.dataset.to, ".schema-port-in");
    if (!start || !end) return;

    const horizontalDistance = end.x - start.x;
    const direction = Math.abs(horizontalDistance) < 40 ? -1 : Math.sign(horizontalDistance);
    const curve = Math.max(90, Math.min(180, Math.abs(horizontalDistance) * 0.45));
    const controlStartX = start.x + curve * direction;
    const controlEndX = end.x - curve * direction;
    arrow.setAttribute(
      "d",
      `M ${start.x} ${start.y} C ${controlStartX} ${start.y}, ${controlEndX} ${end.y}, ${end.x} ${end.y}`,
    );
  });
}

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

window.addEventListener("resize", drawSchemaArrows);
drawSchemaArrows();
selectSchemaTable("appointments");
