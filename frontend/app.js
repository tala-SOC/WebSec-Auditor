// =====================================================
// WEBSEC AUDITOR - FRONTEND
// =====================================================

const urlInput = document.getElementById("urlInput");
const scanButton = document.getElementById("scanButton");
const ctaButton = document.getElementById("ctaButton");


// =====================================================
// SCAN WEBSITE
// =====================================================

scanButton.addEventListener("click", async () => {

    const url = urlInput.value.trim();


    // -------------------------------------------------
    // Validate URL
    // -------------------------------------------------

    if (!url) {

        alert("Please enter a website URL.");

        urlInput.focus();

        return;
    }


    // -------------------------------------------------
    // Loading State
    // -------------------------------------------------

    const originalText = scanButton.textContent;

    scanButton.disabled = true;

    scanButton.textContent = "Scanning...";


    try {

        // -------------------------------------------------
        // Send Scan Request
        // -------------------------------------------------

        const response = await fetch("/scan", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url: url
            })

        });


        // -------------------------------------------------
        // Handle Backend Error
        // -------------------------------------------------

        if (!response.ok) {

            let errorMessage = "Scan failed.";

            try {

                const errorData = await response.json();

                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }

            } catch (error) {
                // Ignore JSON parsing error
            }

            throw new Error(errorMessage);
        }


        // -------------------------------------------------
        // Read Result
        // -------------------------------------------------

        const data = await response.json();


        // -------------------------------------------------
        // Store Result
        // -------------------------------------------------

        localStorage.setItem(
            "websecScanResult",
            JSON.stringify(data)
        );


        // -------------------------------------------------
        // Go To Results
        // -------------------------------------------------

        window.location.href = "/results";


    } catch (error) {

        console.error("Scan error:", error);

        alert(
            "Unable to complete the scan.\n\n" +
            error.message
        );


    } finally {

        scanButton.disabled = false;

        scanButton.textContent = originalText;

    }

});


// =====================================================
// CTA BUTTON
// =====================================================

if (ctaButton) {

    ctaButton.addEventListener("click", () => {

        if (urlInput) {

            urlInput.focus();

        }

    });

}