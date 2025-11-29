// ===================== CONFIG =====================
const BACKEND_URL = "http://127.0.0.1:5000/predict";


// Grab elements (they only exist on frontend.html)
const input = document.getElementById("imageInput");
const dropzone = document.getElementById("dropzone");
const selectBtn = document.getElementById("selectBtn");
const submitBtn = document.getElementById("submitBtn");
const preview = document.getElementById("preview");
const filenameEl = document.getElementById("filename");
const errorMsg = document.getElementById("errorMsg");
const statusMsg = document.getElementById("statusMsg");
const resetBtn = document.getElementById("resetBtn");

// If we're on a page like team_members.html or documentation.html,
// these elements won't exist. In that case, do nothing.
if (
  input &&
  dropzone &&
  selectBtn &&
  submitBtn &&
  preview &&
  filenameEl &&
  errorMsg &&
  statusMsg &&
  resetBtn
) {
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
    selectedFile = null;
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
      filenameEl.textContent =
        file.name + ` (${Math.round(file.size / 1024)} KB)`;
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

  // ----- Event wiring -----

  // Clicking "Choose image"
  selectBtn.addEventListener("click", () => input.click());

  // File chosen via input
  input.addEventListener("change", (e) => handleFiles(e.target.files));

  // Drag & drop UI
  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("is-dragover");
    })
  );

  ["dragleave", "drop"].forEach((evt) =>
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

  // Allow pasting image data
  dropzone.addEventListener("paste", (e) => {
    const items = e.clipboardData?.files;
    if (items && items.length) handleFiles(items);
  });

  // ----- Submit: send image to backend -----
  submitBtn.addEventListener("click", async () => {
    clearMessages();

    if (!selectedFile) {
      errorMsg.textContent = "Please choose an image first.";
      return;
    }

    // UI state
    statusMsg.textContent = "Running AI prediction...";
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", selectedFile); // key name must be "file"

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        statusMsg.textContent = "";
        errorMsg.textContent = `Server error (status ${res.status}).`;
        submitBtn.disabled = false;
        return;
      }

      const data = await res.json();

      if (data.error) {
        statusMsg.textContent = "";
        errorMsg.textContent = "Error: " + data.error;
      } else {
        const pred = data.prediction ?? "Unknown";
        const conf =
          data.confidence != null
            ? ` (${(data.confidence * 100).toFixed(1)}% confidence)`
            : "";

        // Main prediction line
        statusMsg.textContent = `Prediction: ${pred}${conf}`;

        // If you want, you can also log the top5 in the console:
        if (Array.isArray(data.top5)) {
          console.log("Top-5 predictions:", data.top5);
        }
      }
    } catch (err) {
      console.error(err);
      statusMsg.textContent = "";
      errorMsg.textContent =
        "Network error. Is the backend (python app.py) still running?";
    } finally {
      submitBtn.disabled = false;
    }
  });

  // Reset / submit another image
  resetBtn.addEventListener("click", () => {
    selectedFile = null;
    clearMessages();
    showDropzoneUI();
  });

  // Initial UI state
  showDropzoneUI();
}
