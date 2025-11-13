const input = document.getElementById("imageInput");
const dropzone = document.getElementById("dropzone");
const selectBtn = document.getElementById("selectBtn");
const submitBtn = document.getElementById("submitBtn");
const preview = document.getElementById("preview");
const filenameEl = document.getElementById("filename");
const errorMsg = document.getElementById("errorMsg");
const statusMsg = document.getElementById("statusMsg");
const resetBtn = document.getElementById("resetBtn");

let selectedFile = null;

function clearMessages() {
  errorMsg.textContent = "";
  statusMsg.textContent = "";
}

function showPreviewUI() {
  dropzone.style.display = "none";
  preview.style.display = "block";
  resetBtn.style.display = "inline-block";
}

function showDropzoneUI() {
  dropzone.style.display = "block";
  preview.style.display = "none";
  preview.src = "";
  filenameEl.textContent = "";
  resetBtn.style.display = "none";
  submitBtn.disabled = true;
}

function setPreview(file) {
  clearMessages();
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    errorMsg.textContent = "Please select an image file (png, jpg, etc.).";
    preview.style.display = "none";
    preview.src = "";
    filenameEl.textContent = "";
    selectedFile = null;
    submitBtn.disabled = true;
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    filenameEl.textContent = file.name + ` (${Math.round(file.size / 1024)} KB)`;
    selectedFile = file;
    submitBtn.disabled = false;
    showPreviewUI();
  };
  reader.readAsDataURL(file);
}

function handleFiles(files) {
  if (!files || files.length === 0) return;
  setPreview(files[0]);
}

selectBtn.addEventListener("click", () => input.click());
input.addEventListener("change", (e) => handleFiles(e.target.files));

["dragenter", "dragover"].forEach(evt =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.add("is-dragover");
  })
);

["dragleave", "drop"].forEach(evt =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (evt === "dragleave") dropzone.classList.remove("is-dragover");
  })
);

dropzone.addEventListener("drop", (e) => {
  dropzone.classList.remove("is-dragover");
  const dt = e.dataTransfer;
  if (dt && dt.files) handleFiles(dt.files);
});

dropzone.addEventListener("paste", (e) => {
  const items = e.clipboardData?.files;
  if (items && items.length) handleFiles(items);
});

submitBtn.addEventListener("click", () => {
  clearMessages();
  if (!selectedFile) {
    errorMsg.textContent = "Please choose an image first.";
    return;
  }

  statusMsg.textContent = "Submitted! The AI Model will guess now!";
});

resetBtn.addEventListener("click", () => {
  selectedFile = null;
  clearMessages();
  showDropzoneUI();
});
