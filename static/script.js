document.addEventListener('DOMContentLoaded', () => {

    // ================= ELEMENT SELECTION =================
    const urlInput = document.querySelector('.url-box input');
    const submitBtn = document.querySelector('.url-box button');
    const downloadBtn = document.getElementById('start-download');

    const progressBar = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const progressContainer = document.querySelector('.progress-container');

    const previewMedia = document.querySelector('.preview-media');
    const sourceSite = document.querySelector('.source-group strong');
    const videoMeta = document.querySelector('.meta-group strong');

    // ================= THEME & DROPDOWN =================
    const themeSwitch = document.querySelector('.theme-switch');
    if (themeSwitch) {
        themeSwitch.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');
        });
    }

    const downloadManager = document.querySelector('.download-managers');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    if (downloadManager && dropdownMenu) {
        downloadManager.addEventListener('click', e => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show-dropdown');
        });
        document.addEventListener('click', () => {
            dropdownMenu.classList.remove('show-dropdown');
        });
    }

    // ================= 1. PREVIEW LOGIC (NO BLOCKING) =================
    if (submitBtn) {
        submitBtn.addEventListener('click', async e => {
            e.preventDefault();

            const url = urlInput.value.trim();
            if (!url) {
                alert("Please enter a link first!");
                return;
            }

            // UI Reset
            previewMedia.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin fa-3x" style="color:#00f2ff;"></i>
                <p>Fetching Preview...</p>
            `;
            if(sourceSite) sourceSite.innerText = "Loading...";
            if(videoMeta) videoMeta.innerText = "--";

            try {
                const response = await fetch("/preview", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();

                if (data.success) {
                    // Success UI
                    previewMedia.innerHTML = `
                        <img src="${data.thumbnail}" 
                             style="width:100%; height:100%; border-radius:15px; object-fit:cover;">
                    `;
                    if (sourceSite) sourceSite.innerText = data.title || "Unknown Title";
                    if (videoMeta) videoMeta.innerText = data.meta || "Ready to download";
                } else {
                    // Error UI
                    previewMedia.innerHTML = `<i class="fa-solid fa-circle-exclamation fa-3x" style="color:red;"></i><p>Preview Failed</p>`;
                    if (sourceSite) sourceSite.innerText = "Error";
                    console.error("Preview Error:", data);
                }

            } catch (err) {
                console.error(err);
                previewMedia.innerHTML = `<p>Server Connection Error</p>`;
            }
        });
    }

    // ================= 2. DOWNLOAD LOGIC (NO BLOCKING) =================
    if (downloadBtn) {
        downloadBtn.addEventListener('click', async e => {
            e.preventDefault();

            const url = urlInput.value.trim();
            if (!url) {
                alert("Please enter a link first!");
                return;
            }

            // Format Selection
            const formatDropdown = document.getElementById('video-format');
            let selectedFormat = "mp4";
            if (formatDropdown) {
                selectedFormat = formatDropdown.value; // simple value check
            }

            // UI Update
            downloadBtn.disabled = true;
            downloadBtn.innerText = "PROCESSING...";
            
            // Show Progress
            if(progressContainer) {
                progressContainer.style.display = "block";
                progressBar.style.width = "30%";
                progressText.innerText = "Connecting to server...";
            }

            try {
                const response = await fetch("/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        url: url,
                        format: selectedFormat
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Success
                    if(progressBar) progressBar.style.width = "100%";
                    if(progressText) progressText.innerText = "Download Starting...";
                    
                    // Trigger Download
                    const a = document.createElement('a');
                    a.href = `/file/${data.filename}`;
                    a.download = data.filename;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    
                    // Reset Button
                    setTimeout(() => {
                        downloadBtn.disabled = false;
                        downloadBtn.innerText = "DOWNLOAD NOW";
                        if(progressContainer) progressContainer.style.display = "none";
                    }, 3000);

                } else {
                    // Failed
                    alert("Download Failed: " + (data.error || "Check logs"));
                    downloadBtn.disabled = false;
                    downloadBtn.innerText = "DOWNLOAD NOW";
                    if(progressContainer) progressContainer.style.display = "none";
                }

            } catch (err) {
                console.error(err);
                alert("Server Connection Failed!");
                downloadBtn.disabled = false;
                downloadBtn.innerText = "DOWNLOAD NOW";
            }
        });
    }
    
    // Cloud Upload & Settings Logic (যা ছিল তাই রাখা হলো)
    const uploadTrigger = document.getElementById('upload-trigger-btn');
    const fileInput = document.getElementById('cloud-file-input');
    if (uploadTrigger && fileInput) {
        uploadTrigger.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async () => {
             // ... cloud upload logic remains same ...
        });
    }
});