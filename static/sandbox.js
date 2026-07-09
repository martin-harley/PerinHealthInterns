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

function formatSqlForPreview(sql) {
  if (!sql.trim()) return "Start by adding SELECT";
  const normalizedSql = sql.replace(/\s+/g, " ").trim();
  return normalizedSql.replace(
    /\s+(FROM|JOIN|ON|WHERE|SET|VALUES|ORDER BY)\b/g,
    "\n$1",
  );
}

function updateBuilder() {
  if (!builderInput || !chipBoard || !sqlPreview) return;
  const sql = composeSql();
  builderInput.value = sql;
  sqlPreview.textContent = formatSqlForPreview(sql);
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

const relationshipTokens = document.querySelectorAll(".relationship-token");
const relationshipDrops = document.querySelectorAll(".relationship-drop");
const relationshipFeedback = document.querySelector("#relationship-feedback");

function updateRelationshipFeedback() {
  if (!relationshipFeedback) return;
  const correctCount = document.querySelectorAll(".relationship-drop.is-correct").length;
  relationshipFeedback.textContent =
    correctCount === relationshipDrops.length
      ? "All links are correct. This is the schema behind your JOINs."
      : `${correctCount} of ${relationshipDrops.length} links matched.`;
}

relationshipTokens.forEach((token) => {
  token.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain", token.dataset.target);
    event.dataTransfer.setData("text/label", token.textContent);
  });
});

relationshipDrops.forEach((drop) => {
  drop.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  drop.addEventListener("drop", (event) => {
    event.preventDefault();
    const target = event.dataTransfer.getData("text/plain");
    const label = event.dataTransfer.getData("text/label");
    drop.classList.remove("is-correct", "is-wrong");
    if (target === drop.dataset.accept) {
      drop.classList.add("is-correct");
      drop.querySelector("span").textContent = label;
    } else {
      drop.classList.add("is-wrong");
      drop.querySelector("span").textContent = "Not that one. Try a different key.";
    }
    updateRelationshipFeedback();
  });
});
