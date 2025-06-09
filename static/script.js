    const trainBtn = document.getElementById("trainBtn");
    const loadingSpinner = document.getElementById("loadingSpinner");
    const uploadForm = document.getElementById("uploadForm");
    const uploadMessage = document.getElementById("uploadMessage");
    const popup = document.getElementById("popup");

    function showPopup(message, type = "success") {
      popup.textContent = message;
      popup.className = "popup " + type;
      popup.style.opacity = "1";
      popup.style.pointerEvents = "auto";

      setTimeout(() => {
        popup.style.opacity = "0";
        popup.style.pointerEvents = "none";
      }, 4000);
    }

    trainBtn.addEventListener("click", async () => {
      trainBtn.disabled = true;
      loadingSpinner.style.display = "block";
      uploadMessage.textContent = "";

      try {
        const response = await fetch("/train");

        loadingSpinner.style.display = "none";
        trainBtn.disabled = false;

        if (response.ok) {
          showPopup("Training completed successfully!", "success");
        } else {
          showPopup("Training failed. Please try again.", "error");
        }
      } catch (error) {
        loadingSpinner.style.display = "none";
        trainBtn.disabled = false;
        showPopup("Error during training: " + error.message, "error");
      }
    });

    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      uploadMessage.textContent = "";
      const fileInput = document.getElementById("csvFile");
      if (!fileInput.files.length) {
        uploadMessage.textContent = "Please select a CSV file to upload.";
        uploadMessage.className = "text-danger";
        return;
      }

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      try {
        const response = await fetch("/predict", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const text = await response.text();
          const blob = new Blob([text], { type: "text/html" });
          const url = URL.createObjectURL(blob);
          window.location.href = url;
        } else {
          uploadMessage.textContent = "Prediction failed.";
          uploadMessage.className = "text-danger";
        }
      } catch (error) {
        uploadMessage.textContent = "Error during prediction: " + error.message;
        uploadMessage.className = "text-danger";
      }
    });