const input = document.getElementById("imageInput");
const dropzone = document.getElementById("dropzone");
const selectBtn = document.getElementById("selectBtn");
const submitBtn = document.getElementById("submitBtn");
const preview2 = document.getElementById("preview");
const filenameEl = document.getElementById("filename");
const errorMsg = document.getElementById("errorMsg");
const statusMsg = document.getElementById("statusMsg");

// Keep the selected file in memory for submit
let selectedFile = null;

// --- Helpers ---
function clearMessages() {
  errorMsg.textContent = "";
  statusMsg.textContent = "";
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
    preview.style.display = "block";
    filenameEl.textContent = file.name + ` (${Math.round(file.size / 1024)} KB)`;
    selectedFile = file;
    submitBtn.disabled = false;
  };
  reader.readAsDataURL(file);
}

function handleFiles(files) {
  if (!files || files.length === 0) return;
  setPreview(files[0]); // show the first image
}

// --- Input select (button triggers hidden input) ---
selectBtn.addEventListener("click", () => input.click());
input.addEventListener("change", (e) => handleFiles(e.target.files));

// --- Drag & drop ---
;["dragenter", "dragover"].forEach(evt =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.add("is-dragover");
  })
);

;["dragleave", "drop"].forEach(evt =>
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

// --- Submit (stub) ---
// Replace '/upload' with your backend endpoint
//currently just a demo
submitBtn.addEventListener("click", async () => {
  clearMessages();
  if (!selectedFile) {
    errorMsg.textContent = "Please choose an image first.";
    return;
  }

  // Example: send to backend
  // const formData = new FormData();
  // formData.append("image", selectedFile);
  // try {
  //   statusMsg.textContent = "Uploading...";
  //   const res = await fetch("/upload", { method: "POST", body: formData });
  //   if (!res.ok) throw new Error(`Upload failed (${res.status})`);
  //   const data = await res.json(); // e.g., { label: "tiger", confidence: 0.92 }
  //   statusMsg.textContent = `Uploaded! Predicted: ${data.label} (${(data.confidence*100).toFixed(1)}%)`;
  // } catch (err) {
  //   errorMsg.textContent = err.message || "Upload failed.";
  // }

  //simulate success
  statusMsg.textContent = "Submitted! (Demo: this will be wired to our AI model)";
});