// ===================== CONFIG =====================
const BACKEND_URL = "http://127.0.0.1:5000/predict";

// Grab elements
const input = document.getElementById("imageInput");
const dropzone = document.getElementById("dropzone");
const selectBtn = document.getElementById("selectBtn");
const submitBtn = document.getElementById("submitBtn");
const preview = document.getElementById("preview");
const filenameEl = document.getElementById("filename");
const errorMsg = document.getElementById("errorMsg");
const statusMsg = document.getElementById("statusMsg");
const resetBtn = document.getElementById("resetBtn");

// Check if core elements exist (only on frontend.html)
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
  
  // Get or create results container
  let resultsContainer = document.getElementById("resultsContainer");
  if (!resultsContainer) {
    resultsContainer = document.createElement("div");
    resultsContainer.id = "resultsContainer";
    resultsContainer.style.display = "none";
    // Insert after statusMsg
    statusMsg.parentNode.insertBefore(resultsContainer, statusMsg.nextSibling);
  }

  function clearMessages() {
    errorMsg.textContent = "";
    statusMsg.textContent = "";
    resultsContainer.innerHTML = "";
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
    resultsContainer.innerHTML = "";
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

  function displayResults(data) {
    resultsContainer.innerHTML = "";

    // Display taxonomy level info if not species level
    const taxLevel = data.taxonomy_level;
    if (taxLevel && taxLevel.tax_level !== "species") {
      const taxWarning = document.createElement("div");
      taxWarning.className = "taxonomy-warning";
      taxWarning.innerHTML = `
        <p><strong>Note:</strong> Confidence was below threshold for species-level classification.</p>
        <p>Best match at <strong>${taxLevel.tax_level}</strong> level: 
          <em>${taxLevel.name || 'Unknown'}</em> 
          (${(taxLevel.confidence * 100).toFixed(1)}% confidence)
        </p>
      `;
      resultsContainer.appendChild(taxWarning);
    }

    // Main prediction section
    const mainResult = document.createElement("div");
    mainResult.className = "main-result";
    
    const wiki = data.wikipedia || {};
    const confidencePercent = (data.confidence * 100).toFixed(1);

    mainResult.innerHTML = `
      <h2>Top Prediction: ${data.prediction}</h2>
      <p class="confidence">Confidence: ${confidencePercent}%</p>
      
      ${wiki.thumbnail ? `<img src="${wiki.thumbnail}" alt="${wiki.title}" class="wiki-thumbnail" />` : ''}
      
      <div class="wiki-summary">
        <p>${wiki.summary || 'No summary available.'}</p>
        ${wiki.url ? `<a href="${wiki.url}" target="_blank" rel="noopener">Read more on Wikipedia →</a>` : ''}
      </div>
    `;
    
    resultsContainer.appendChild(mainResult);

    // Alternative predictions section
    if (data.top5 && data.top5.length > 1) {
      const alternativesSection = document.createElement("div");
      alternativesSection.className = "alternatives-section";
      
      const header = document.createElement("h3");
      header.textContent = "If this doesn't look right, it might be one of these:";
      alternativesSection.appendChild(header);

      const alternativesList = document.createElement("div");
      alternativesList.className = "alternatives-list";

      // Skip the first one (already shown above)
      data.top5.slice(1).forEach((item) => {
        const altDiv = document.createElement("div");
        altDiv.className = "alternative-item";
        
        const prob = (item.prob * 100).toFixed(1);

        altDiv.innerHTML = `
          <div class="alt-header">
            <strong>${item.species}</strong>
            <span class="alt-prob">${prob}%</span>
          </div>
          ${item.wiki_image ? `<img src="${item.wiki_image}" alt="${wiki.title}" class="wiki-thumbnail" />` : ''}
        `;
        
        alternativesList.appendChild(altDiv);
      });

      alternativesSection.appendChild(alternativesList);
      resultsContainer.appendChild(alternativesSection);
    }

    resultsContainer.style.display = "block";
  }

  // ----- Event wiring -----

  selectBtn.addEventListener("click", () => input.click());

  input.addEventListener("change", (e) => handleFiles(e.target.files));

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

  dropzone.addEventListener("paste", (e) => {
    const items = e.clipboardData?.files;
    if (items && items.length) handleFiles(items);
  });

  // ----- Submit: send image to backend -----
  submitBtn.addEventListener("click", async () => {
    console.log("Submit button clicked");
    clearMessages();

    if (!selectedFile) {
      errorMsg.textContent = "Please choose an image first.";
      return;
    }

    statusMsg.textContent = "Running AI prediction...";
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      console.log("Sending request to:", BACKEND_URL);
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", res.status);

      if (!res.ok) {
        const errorText = await res.text();
        console.error("Server error response:", errorText);
        statusMsg.textContent = "";
        errorMsg.textContent = `Server error (status ${res.status}). Check console for details.`;
        submitBtn.disabled = false;
        return;
      }

      const data = await res.json();
      console.log("Response data:", data);

      if (data.error) {
        statusMsg.textContent = "";
        errorMsg.textContent = "Error: " + data.error;
      } else {
        statusMsg.textContent = "Prediction complete!";
        displayResults(data);
      }
    } catch (err) {
      console.error("Fetch error:", err);
      statusMsg.textContent = "";
      errorMsg.textContent =
        "Network error. Is the backend (python app.py) still running?";
    } finally {
      submitBtn.disabled = false;
    }
  });

  resetBtn.addEventListener("click", () => {
    selectedFile = null;
    clearMessages();
    showDropzoneUI();
  });

  // Initial UI state
  showDropzoneUI();
  
  console.log("Script loaded successfully");
}