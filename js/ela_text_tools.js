// Ela Text Tools - frontend extension
// Ela Text Concat node'unda sadece `count` kadar metin slotu gosterir,
// altina "+ satir" / "- satir" butonlari ekler.

import { app } from "../../scripts/app.js";

const MAX_SLOTS = 12;
const SLOT_RE = /^text_(\d+)$/;

function getCountWidget(node) {
  return node.widgets?.find((w) => w.name === "count");
}

function getSlotWidgets(node) {
  const found = [];
  for (const w of node.widgets ?? []) {
    const match = SLOT_RE.exec(w.name ?? "");
    if (match) found.push({ widget: w, index: Number(match[1]) });
  }
  found.sort((a, b) => a.index - b.index);
  return found;
}

function hideWidget(widget) {
  if (widget.__elaHidden) return;
  widget.__elaHidden = {
    type: widget.type,
    computeSize: widget.computeSize,
  };
  widget.type = "hidden";
  widget.computeSize = () => [0, -4];
  if (widget.element) widget.element.style.display = "none";
  if (widget.inputEl) widget.inputEl.style.display = "none";
}

function showWidget(widget) {
  if (!widget.__elaHidden) return;
  widget.type = widget.__elaHidden.type;
  widget.computeSize = widget.__elaHidden.computeSize;
  if (widget.element) widget.element.style.display = "";
  if (widget.inputEl) widget.inputEl.style.display = "";
  delete widget.__elaHidden;
}

function applyLayout(node, resize = true) {
  const countWidget = getCountWidget(node);
  if (!countWidget) return;

  let count = Math.round(Number(countWidget.value) || 1);
  count = Math.max(1, Math.min(MAX_SLOTS, count));
  if (Number(countWidget.value) !== count) countWidget.value = count;

  for (const { widget, index } of getSlotWidgets(node)) {
    if (index <= count) showWidget(widget);
    else hideWidget(widget);
  }

  if (resize) {
    const [minWidth, minHeight] = node.computeSize();
    node.setSize([Math.max(node.size[0], minWidth, 360), minHeight]);
  }
  node.setDirtyCanvas(true, true);
}

function setCount(node, delta) {
  const countWidget = getCountWidget(node);
  if (!countWidget) return;
  const next = Math.max(1, Math.min(MAX_SLOTS, Math.round(Number(countWidget.value) || 1) + delta));
  if (next === Number(countWidget.value)) return;
  countWidget.value = next;
  applyLayout(node);
}

// DOM widgetlar Vue tarafinda gec olusabiliyor; birkac kez tekrar dene.
function scheduleLayout(node) {
  for (const delay of [0, 120, 400]) {
    setTimeout(() => applyLayout(node), delay);
  }
}

function install(node) {
  if (node.__elaTextConcat) return;
  node.__elaTextConcat = true;

  const countWidget = getCountWidget(node);
  if (countWidget) {
    const original = countWidget.callback;
    countWidget.callback = function (...args) {
      const result = original?.apply(this, args);
      applyLayout(node);
      return result;
    };
  }

  const addButton = node.addWidget("button", "+ satir", null, () => setCount(node, +1));
  addButton.serialize = false;
  const removeButton = node.addWidget("button", "- satir", null, () => setCount(node, -1));
  removeButton.serialize = false;

  applyLayout(node);
  scheduleLayout(node);
}

app.registerExtension({
  name: "Ela.TextTools",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== "ElaTextConcat") return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function (...args) {
      const result = onNodeCreated?.apply(this, args);
      install(this);
      return result;
    };

    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function (...args) {
      const result = onConfigure?.apply(this, args);
      install(this);
      applyLayout(this);
      scheduleLayout(this);
      return result;
    };
  },
});
