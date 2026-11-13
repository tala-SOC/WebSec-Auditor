// =====================================================
// WEBSEC AUDITOR - FRONTEND
// =====================================================
 
const urlInput = document.getElementById("urlInput");
const scanButton = document.getElementById("scanButton");
const ctaButton = document.getElementById("ctaButton");
const card = document.getElementById("securityCard");
const cardStatus = document.getElementById("cardStatus");
 
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
 
 
// =====================================================
// SCAN WEBSITE
// =====================================================
 
function setScanning(on) {
    const label = scanButton.querySelector(".label");
 
    scanButton.disabled = on;
    label.textContent = on ? "Scanning..." : "Scan Website";
 
    if (card) card.classList.toggle("scanning", on);
    if (cardStatus) cardStatus.textContent = on ? "Scanning..." : "Ready to Scan";
}
 
if (scanButton) {
 
    scanButton.addEventListener("click", async () => {
 
        const url = urlInput.value.trim();
 
        if (!url) {
            alert("Please enter a website URL.");
            urlInput.focus();
            return;
        }
 
        setScanning(true);
 
        try {
 
            const response = await fetch("/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });
 
            if (!response.ok) {
 
                let message = "Scan failed.";
 
                try {
                    const err = await response.json();
                    if (err.detail) message = err.detail;
                } catch (_) { /* ignore */ }
 
                throw new Error(message);
            }
 
            const data = await response.json();
 
            localStorage.setItem("websecScanResult", JSON.stringify(data));
 
            window.location.href = "/results";
 
        } catch (error) {
 
            console.error("Scan error:", error);
            alert("Unable to complete the scan.\n\n" + error.message);
            setScanning(false);
        }
    });
 
    // Enter يشغّل الفحص
    urlInput.addEventListener("keydown", e => {
        if (e.key === "Enter") scanButton.click();
    });
}
 
 
// =====================================================
// CTA BUTTON: يطلع للأعلى ويركّز على الحقل
// =====================================================
 
if (ctaButton && urlInput) {
 
    ctaButton.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
        setTimeout(() => urlInput.focus(), 500);
    });
}
 
 
// =====================================================
// EFFECT 1: شبكة نقاط تتفاعل مع الماوس
// =====================================================
 
const canvas = document.getElementById("bg-canvas");
 
if (canvas && !reduceMotion) {
 
    const ctx = canvas.getContext("2d");
    const mouse = { x: -9999, y: -9999 };
    const LINK = 130, REACH = 170;
 
    let w, h, nodes = [];
 
    function resize() {
        const dpr = window.devicePixelRatio || 1;
 
        w = window.innerWidth;
        h = window.innerHeight;
 
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
 
        const count = Math.min(80, Math.floor((w * h) / 18000));
 
        nodes = Array.from({ length: count }, () => ({
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4
        }));
    }
 
    window.addEventListener("resize", resize);
 
    window.addEventListener("mousemove", e => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
 
    document.addEventListener("mouseleave", () => {
        mouse.x = mouse.y = -9999;
    });
 
    function line(x1, y1, x2, y2, alpha, color) {
        ctx.strokeStyle = `rgba(${color},${alpha})`;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    }
 
    function draw() {
        ctx.clearRect(0, 0, w, h);
 
        for (let i = 0; i < nodes.length; i++) {
            const a = nodes[i];
 
            a.x += a.vx;
            a.y += a.vy;
 
            if (a.x < 0 || a.x > w) a.vx *= -1;
            if (a.y < 0 || a.y > h) a.vy *= -1;
 
            ctx.beginPath();
            ctx.arc(a.x, a.y, 1.6, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(40,199,183,.6)";
            ctx.fill();
 
            for (let j = i + 1; j < nodes.length; j++) {
                const b = nodes[j];
                const d = Math.hypot(a.x - b.x, a.y - b.y);
 
                if (d < LINK) line(a.x, a.y, b.x, b.y, 0.16 * (1 - d / LINK), "40,199,183");
            }
 
            const dm = Math.hypot(a.x - mouse.x, a.y - mouse.y);
 
            if (dm < REACH) {
                line(a.x, a.y, mouse.x, mouse.y, 0.4 * (1 - dm / REACH), "105,224,210");
                a.x += (mouse.x - a.x) * 0.004;
                a.y += (mouse.y - a.y) * 0.004;
            }
        }
 
        requestAnimationFrame(draw);
    }
 
    resize();
    draw();
}
 
 
// =====================================================
// EFFECT 2: روابط وكلمات أمنية تطير للأعلى
// =====================================================
 
const chipsBox = document.getElementById("chips");
 
if (chipsBox && !reduceMotion) {
 
    [
        "https://", "HSTS", "Content-Security-Policy", "HttpOnly", "Secure",
        "SameSite", "X-Frame-Options", "CORS", "Set-Cookie",
        "X-Content-Type-Options", "Referrer-Policy", "TLS 1.3"
    ].forEach(text => {
 
        const chip = document.createElement("span");
        const duration = 16 + Math.random() * 14;
 
        chip.className = "chip";
        chip.textContent = text;
        chip.style.left = Math.random() * 90 + "%";
        chip.style.setProperty("--drift", (Math.random() * 160 - 80) + "px");
        chip.style.animationDuration = duration + "s";
        chip.style.animationDelay = "-" + Math.random() * duration + "s";
 
        chipsBox.appendChild(chip);
    });
}
 
 
// =====================================================
// EFFECT 3: البطاقة تميل مع الماوس
// =====================================================
 
const hero = document.querySelector(".hero");
 
if (card && hero && !reduceMotion) {
 
    hero.addEventListener("mousemove", e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - (r.left + r.width / 2)) / (window.innerWidth / 2);
        const y = (e.clientY - (r.top + r.height / 2)) / (window.innerHeight / 2);
 
        card.style.transform =
            `perspective(900px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg)`;
    });
 
    hero.addEventListener("mouseleave", () => {
        card.style.transform = "";
    });
}
 
 
// =====================================================
// EFFECT 4: توهج يتبع الماوس داخل بطاقات الميزات
// =====================================================
 
document.querySelectorAll(".feature-card").forEach(el => {
 
    el.addEventListener("mousemove", e => {
        const r = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - r.left) + "px");
        el.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
});
 
 
// =====================================================
// EFFECT 5: ظهور العناصر عند النزول
// =====================================================
 
if ("IntersectionObserver" in window && !reduceMotion) {
 
    const targets = document.querySelectorAll(
        ".section-heading, .feature-card, .step, .cta-content"
    );
 
    const io = new IntersectionObserver(entries => {
 
        entries.forEach(entry => {
 
            if (!entry.isIntersecting) return;
 
            const el = entry.target;
 
            el.classList.add("in");
            io.unobserve(el);
 
            // بعد الظهور نشيل الكلاسات عشان ما تتعارض مع حركة الـ hover
            setTimeout(() => {
                el.classList.remove("reveal", "in");
                el.style.transitionDelay = "";
            }, 900);
        });
 
    }, { threshold: 0.15 });
 
    targets.forEach((el, i) => {
        el.classList.add("reveal");
        el.style.transitionDelay = (i % 4) * 90 + "ms";
        io.observe(el);
    });
}
 