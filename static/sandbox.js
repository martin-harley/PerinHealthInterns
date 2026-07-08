const blocks = document.querySelectorAll(".sql-block");
const builder = document.querySelector("#builder-sql");

function appendSql(sql) {
  if (!builder) return;
  const separator = builder.value.trim() ? "\n" : "";
  builder.value = `${builder.value}${separator}${sql}`;
  builder.focus();
}

blocks.forEach((block) => {
  block.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain", block.dataset.sql);
  });

  block.addEventListener("click", () => {
    appendSql(block.dataset.sql);
  });
});

if (builder) {
  builder.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  builder.addEventListener("drop", (event) => {
    event.preventDefault();
    appendSql(event.dataTransfer.getData("text/plain"));
  });
}

document.querySelectorAll("[data-clear-target]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.getElementById(button.dataset.clearTarget);
    if (target) target.value = "";
  });
});
