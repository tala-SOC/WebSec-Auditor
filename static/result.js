
document.addEventListener("DOMContentLoaded", () => {

    const $ = (id) => document.getElementById(id);

    const findingsList = $("findingsList");
    const emptyState = $("emptyState");

    let findings = [];
    let currentFilter = "ALL";
    let searchQuery = "";

    // ==========================================
    // LOAD RESULT
    // ==========================================

    const storedResult = localStorage.getItem("websecScanResult");

    if (!storedResult) {
        $("scannedUrl").textContent = "No scan result found.";
        $("scoreStatus").textContent = "No Report Available";
        findingsList.innerHTML = "";
        emptyState.hidden = false;
        emptyState.querySelector("h3").textContent = "No scan data found";
        emptyState.querySelector("p").textContent =
            "Please return to the homepage and scan a website.";
        return;
    }

    let data;

    try {
        data = JSON.parse(storedResult);

        if (!data || !Array.isArray(data.findings)) {
            throw new Error("Invalid scan result format.");
        }

    } catch (error) {
        console.error("Result parsing error:", error);

        $("scannedUrl").textContent = "Unable to load scan information.";
        $("scoreStatus").textContent = "Invalid Report";
        findingsList.innerHTML = "";
        emptyState.hidden = false;

        return;
    }

    findings = data.findings;

    // ==========================================
    // URL AND DATE
    // ==========================================

    $("scannedUrl").textContent = data.url || "Unknown website";

    $("scanDate").textContent =
        new Date().toLocaleString();

    // ==========================================
    // COUNTS
    // ==========================================

    let passed = 0;
    let issues = 0;
    let high = 0;
    let medium = 0;
    let low = 0;

    findings.forEach(finding => {

        if (finding.status === "PASS") {
            passed++;
        } else {
            issues++;

            if (finding.severity === "HIGH") high++;
            if (finding.severity === "MEDIUM") medium++;
            if (finding.severity === "LOW") low++;
        }

    });

    $("passedCount").textContent = passed;
    $("issueCount").textContent = issues;
    $("highCount").textContent = high;
    $("mediumCount").textContent = medium;
    $("lowCount").textContent = low;

    $("findingsTotal").textContent =
        `${findings.length} CHECKS`;

    // ==========================================
    // SECURITY SCORE
    // ==========================================

    const score = Math.max(
        0,
        Math.min(100, Number(data.score) || 0)
    );

    $("securityScore").textContent = score;

    let scoreStatus;
    let scoreDescription;
    let scoreColor;

    if (score >= 80) {
        scoreStatus = "Good";
        scoreDescription = "The website has a relatively strong security configuration.";
        scoreColor = "#28C7B7";

    } else if (score >= 60) {
        scoreStatus = "Fair";
        scoreDescription = "Some security improvements are recommended.";
        scoreColor = "#E5B85C";

    } else {
        scoreStatus = "Needs Improvement";
        scoreDescription = "Several security issues require attention.";
        scoreColor = "#E87979";
    }

    $("scoreStatus").textContent = scoreStatus;
    $("scoreDescription").textContent = scoreDescription;

    $("scoreCircle").style.setProperty(
        "--score-color",
        scoreColor
    );

    $("scoreCircle").style.setProperty(
        "--score",
        "0deg"
    );

    requestAnimationFrame(() => {
        $("scoreCircle").style.setProperty(
            "--score",
            `${score * 3.6}deg`
        );

        $("scoreProgressBar").style.width = `${score}%`;
        $("scoreProgressBar").style.background = scoreColor;
    });

    // ==========================================
    // FINDING CARD CREATOR
    // ==========================================

    function createFindingCard(finding, index) {

        const card = document.createElement("article");

        card.className = "finding-card";
        card.style.animationDelay = `${Math.min(index * 0.06, 0.6)}s`;

        const isPassed = finding.status === "PASS";
        const statusClass = isPassed ? "pass" :
            finding.status === "MISSING" ||
            finding.status === "ERROR" ? "issue" : "info";

        const icon = isPassed ? "✓" :
            finding.status === "MISSING" ? "!" :
            finding.status === "ERROR" ? "×" : "•";

        const iconElement = document.createElement("div");
        iconElement.className = `finding-icon ${statusClass}`;
        iconElement.textContent = icon;

        const content = document.createElement("div");
        content.className = "finding-content";

        const top = document.createElement("div");
        top.className = "finding-top";

        const title = document.createElement("h3");
        title.textContent = finding.name || "Security Check";

        const badges = document.createElement("div");
        badges.className = "finding-badges";

        const statusBadge = document.createElement("span");
        statusBadge.className = `status-badge ${statusClass}`;
        statusBadge.textContent = finding.status || "UNKNOWN";

        const severityBadge = document.createElement("span");
        severityBadge.className = "severity-badge";
        severityBadge.textContent = finding.severity || "INFO";

        badges.append(statusBadge, severityBadge);
        top.append(title, badges);

        const description = document.createElement("p");
        description.textContent =
            finding.description || "No description available.";

        content.append(top, description);

        if (finding.recommendation && !isPassed) {

            const recommendation = document.createElement("div");
            recommendation.className = "recommendation";

            const strong = document.createElement("strong");
            strong.textContent = "Recommendation: ";

            recommendation.append(
                strong,
                document.createTextNode(finding.recommendation)
            );

            content.appendChild(recommendation);
        }

        card.append(iconElement, content);

        return card;
    }

    // ==========================================
    // RENDER FINDINGS
    // ==========================================

    function renderFindings() {

        findingsList.innerHTML = "";

        const filtered = findings.filter(finding => {

            const matchesFilter =
                currentFilter === "ALL" ||
                (currentFilter === "PASS" && finding.status === "PASS") ||
                (currentFilter === "ISSUE" && finding.status !== "PASS");

            const searchableText = [
                finding.name,
                finding.description,
                finding.recommendation,
                finding.status,
                finding.severity
            ].join(" ").toLowerCase();

            const matchesSearch =
                searchableText.includes(searchQuery);

            return matchesFilter && matchesSearch;
        });

        emptyState.hidden = filtered.length !== 0;

        filtered.forEach((finding, index) => {
            findingsList.appendChild(
                createFindingCard(finding, index)
            );
        });
    }

    renderFindings();

    // ==========================================
    // FILTER BUTTONS
    // ==========================================

    document.querySelectorAll(".filter-btn").forEach(button => {

        button.addEventListener("click", () => {

            document.querySelectorAll(".filter-btn").forEach(btn => {
                btn.classList.remove("active");
            });

            button.classList.add("active");

            currentFilter = button.dataset.filter;

            renderFindings();
        });

    });

    // ==========================================
    // SEARCH
    // ==========================================

    $("findingSearch").addEventListener("input", event => {

        searchQuery = event.target.value.trim().toLowerCase();

        renderFindings();

    });

    // ==========================================
    // PRINT REPORT
    // ==========================================

    $("printReport").addEventListener("click", () => {
        window.print();
    });

    // ==========================================
    // NEW SCAN
    // ==========================================

    $("newScan").addEventListener("click", () => {

        localStorage.removeItem("websecScanResult");

        window.location.href = "/";
    });

});
