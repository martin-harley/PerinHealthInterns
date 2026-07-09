const blocks = document.querySelectorAll(".sql-block");
const builderInput = document.querySelector("#builder-sql");
const chipBoard = document.querySelector("#builder-chip-board");
const sqlPreview = document.querySelector("#builder-sql-preview");

function appendWithSpacing(currentSql, fragment) {
  const needsSpace =
    currentSql.length > 0 &&
    !/\s$/.test(currentSql) &&
    !/^[,;)=]/.test(fragment) &&
    fragment !== ")";
  return `${currentSql}${needsSpace ? " " : ""}${fragment}`;
}

function getChips() {
  if (!chipBoard) return [];
  return Array.from(chipBoard.querySelectorAll(".query-chip"));
}

function composeSql() {
  return getChips().reduce(
    (sql, chip) => appendWithSpacing(sql, chip.dataset.sql),
    "",
  );
}

function updateBuilder() {
  if (!builderInput || !chipBoard || !sqlPreview) return;
  const sql = composeSql();
  builderInput.value = sql;
  sqlPreview.textContent = sql || "Start by adding SELECT";
  chipBoard.classList.toggle("is-empty", !sql);
  if (sql) {
    chipBoard.querySelector(".builder-empty")?.remove();
  } else if (!chipBoard.querySelector(".builder-empty")) {
    const empty = document.createElement("p");
    empty.className = "builder-empty";
    empty.textContent = "Drop SQL pieces here";
    chipBoard.appendChild(empty);
  }
}

function addChip(sql) {
  if (!chipBoard || !sql) return;
  chipBoard.querySelector(".builder-empty")?.remove();
  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "query-chip";
  chip.dataset.sql = sql;
  chip.textContent = sql.trim() || sql;
  chip.setAttribute("aria-label", `Remove ${chip.textContent}`);
  chip.addEventListener("click", () => {
    chip.remove();
    updateBuilder();
  });
  chipBoard.appendChild(chip);
  updateBuilder();
}

blocks.forEach((block) => {
  block.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain", block.dataset.sql);
  });

  block.addEventListener("click", () => {
    addChip(block.dataset.sql);
  });
});

if (chipBoard) {
  chipBoard.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  chipBoard.addEventListener("drop", (event) => {
    event.preventDefault();
    addChip(event.dataTransfer.getData("text/plain"));
  });
}

document.querySelectorAll("[data-clear-target]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.getElementById(button.dataset.clearTarget);
    if (target) target.value = "";
    getChips().forEach((chip) => chip.remove());
    updateBuilder();
  });
});

document.querySelector(".sandbox-editor")?.addEventListener("submit", updateBuilder);

if (builderInput?.value) {
  addChip(builderInput.value);
} else {
  updateBuilder();
}
