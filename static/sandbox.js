const blocks = document.querySelectorAll(".sql-block");
const builder = document.querySelector("#builder-sql");

function appendSql(sql) {
  if (!builder) return;
  const start = builder.selectionStart ?? builder.value.length;
  const end = builder.selectionEnd ?? builder.value.length;
  const before = builder.value.slice(0, start);
  const needsSpace =
    before.length > 0 &&
    !/\s$/.test(before) &&
    !/^[,;)=]/.test(sql) &&
    sql !== ")";
  builder.setRangeText(`${needsSpace ? " " : ""}${sql}`, start, end, "end");
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
