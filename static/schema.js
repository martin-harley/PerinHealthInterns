const schemaMap = document.querySelector(".schema-map");
const schemaCanvas = document.querySelector(".schema-canvas");
const schemaTitle = document.querySelector("#schema-detail-title");
const schemaCopy = document.querySelector("#schema-detail-copy");
const schemaProgress = document.querySelector("#schema-progress");
const schemaReset = document.querySelector("#schema-reset");

const dragPorts = document.querySelectorAll("[data-drag]");
const dropPorts = document.querySelectorAll("[data-drop]");

const svgNS = "http://www.w3.org/2000/svg";
const connections = new Map();

function portCenter(port) {
  const portRect = port.getBoundingClientRect();
  const mapRect = schemaMap.getBoundingClientRect();
  return {
    x: portRect.left + portRect.width / 2 - mapRect.left,
    y: portRect.top + portRect.height / 2 - mapRect.top,
  };
}

function bulgeDirection(port) {
  return port.classList.contains("schema-port-right") ? 1 : -1;
}

function nodeBox(port) {
  const node = port.closest(".schema-node");
  const nodeRect = node.getBoundingClientRect();
  const mapRect = schemaMap.getBoundingClientRect();
  return {
    left: nodeRect.left - mapRect.left,
    right: nodeRect.right - mapRect.left,
    bottom: nodeRect.bottom - mapRect.top,
  };
}

function pathFor(fromPort, from, to, toPort) {
  const fromDir = bulgeDirection(fromPort);
  const toDir = toPort ? bulgeDirection(toPort) : -fromDir;
  const reach = Math.max(Math.abs(to.x - from.x) * 0.6, 90);

  if (toPort && Math.abs(from.y - to.y) < 1) {
    const fromBox = nodeBox(fromPort);
    const toBox = nodeBox(toPort);
    const dipY = Math.max(fromBox.bottom, toBox.bottom) + 40;
    const fromClear = fromDir < 0 ? fromBox.left - 20 : fromBox.right + 20;
    const toClear = toDir < 0 ? toBox.left - 20 : toBox.right + 20;

    return [
      `M ${from.x} ${from.y}`,
      `C ${fromClear} ${from.y}, ${fromClear} ${dipY}, ${fromClear} ${dipY}`,
      `L ${toClear} ${dipY}`,
      `C ${toClear} ${dipY}, ${toClear} ${to.y}, ${to.x} ${to.y}`,
    ].join(" ");
  }

  const fromControl = { x: from.x + fromDir * reach, y: from.y };
  const toControl = { x: to.x + toDir * reach, y: to.y };

  return `M ${from.x} ${from.y} C ${fromControl.x} ${fromControl.y}, ${toControl.x} ${toControl.y}, ${to.x} ${to.y}`;
}

function drawLine(fromPort, toPort, state) {
  const from = portCenter(fromPort);
  const to = portCenter(toPort);

  const path = document.createElementNS(svgNS, "path");
  path.setAttribute("d", pathFor(fromPort, from, to, toPort));
  path.setAttribute("class", `schema-line schema-line-${state}`);
  schemaCanvas.appendChild(path);
  return path;
}

function updateProgress() {
  const correctCount = Array.from(connections.values()).filter(
    (entry) => entry.state === "correct"
  ).length;
  schemaProgress.textContent = `${correctCount} of ${dragPorts.length} connected`;

  if (correctCount === dragPorts.length) {
    schemaTitle.textContent = "All connected!";
    schemaCopy.textContent =
      "Every foreign key now points at the right primary key. Reset to practice again.";
  }
}

function clearConnection(fkKey) {
  const existing = connections.get(fkKey);
  if (existing) {
    existing.path.remove();
    connections.delete(fkKey);
  }
}

function connect(fromPort, toPort) {
  const fkKey = fromPort.dataset.drag;
  const answer = fromPort.closest("[data-answer]").dataset.answer;
  const target = toPort.dataset.drop;
  const isCorrect = target === answer;
  const state = isCorrect ? "correct" : "incorrect";

  clearConnection(fkKey);
  const path = drawLine(fromPort, toPort, state);
  connections.set(fkKey, { path, state });

  const label = fromPort.closest("[data-fk]").querySelector("small");
  if (isCorrect) {
    label.textContent = target;
    schemaTitle.textContent = "Correct!";
    schemaCopy.textContent = `${fkKey} correctly references ${target}.`;
  } else {
    label.textContent = "?";
    schemaTitle.textContent = "Not quite";
    schemaCopy.textContent = `${fkKey} does not reference ${target}. Try again.`;
    window.setTimeout(() => {
      if (connections.get(fkKey)?.path === path) {
        clearConnection(fkKey);
      }
    }, 900);
  }

  updateProgress();
}

function resizeCanvas() {
  const mapRect = schemaMap.getBoundingClientRect();
  schemaCanvas.setAttribute("width", mapRect.width);
  schemaCanvas.setAttribute("height", mapRect.height);
}

let dragState = null;

function startDrag(port, event) {
  event.preventDefault();
  resizeCanvas();
  const previewPath = document.createElementNS(svgNS, "path");
  previewPath.setAttribute("class", "schema-line schema-line-preview");
  schemaCanvas.appendChild(previewPath);
  dragState = { port, previewPath };
  document.addEventListener("pointermove", onDragMove);
  document.addEventListener("pointerup", onDragEnd);
}

function onDragMove(event) {
  if (!dragState) return;
  const from = portCenter(dragState.port);
  const mapRect = schemaMap.getBoundingClientRect();
  const to = { x: event.clientX - mapRect.left, y: event.clientY - mapRect.top };
  dragState.previewPath.setAttribute("d", pathFor(dragState.port, from, to));
}

function onDragEnd(event) {
  if (!dragState) return;
  const { port, previewPath } = dragState;
  previewPath.remove();
  document.removeEventListener("pointermove", onDragMove);
  document.removeEventListener("pointerup", onDragEnd);
  dragState = null;

  const dropTarget = document
    .elementsFromPoint(event.clientX, event.clientY)
    .find((el) => el.matches("[data-drop]"));

  if (dropTarget) {
    connect(port, dropTarget);
  }
}

dragPorts.forEach((port) => {
  port.addEventListener("pointerdown", (event) => startDrag(port, event));
});

if (schemaReset) {
  schemaReset.addEventListener("click", () => {
    connections.forEach((entry) => entry.path.remove());
    connections.clear();
    document.querySelectorAll("[data-fk] small").forEach((label) => {
      label.textContent = "?";
    });
    schemaTitle.textContent = "Link the tables";
    schemaCopy.textContent =
      "Drag a line from each foreign key (green outlined dot) to the primary key it references.";
    updateProgress();
  });
}

window.addEventListener("resize", () => {
  resizeCanvas();
  connections.forEach((entry, fkKey) => {
    const fromPort = document.querySelector(`[data-drag="${fkKey}"]`);
    const answer = fromPort.closest("[data-answer]").dataset.answer;
    const toPort = document.querySelector(`[data-drop="${answer}"]`);
    entry.path.remove();
    const newPath = drawLine(fromPort, toPort, entry.state);
    connections.set(fkKey, { path: newPath, state: entry.state });
  });
});

resizeCanvas();
updateProgress();
