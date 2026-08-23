// Tbiliso — Form-Validation, Scroll-Top & Live-Google-Bewertung
document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split("T")[0];
  document.querySelectorAll("input[type=date]").forEach(i => i.min = today);

  const LANG = (document.documentElement.lang || "de").toLowerCase();

  const I18N = {
    de: {
      sending:    "Sende Reservierung …",
      ok:         "✅ Vielen Dank! Ihre Reservierung ist eingegangen. Wir bestätigen sie in Kürze.",
      err_prefix: "❌ ",
      net_err:    "❌ Netzwerkfehler – bitte versuchen Sie es erneut.",
      send_msg:   "Sende Nachricht …",
      msg_ok:     "✅ Vielen Dank für Ihre Nachricht!",
      msg_err:    "❌ Fehler beim Senden.",
    },
    en: {
      sending:    "Sending reservation …",
      ok:         "✅ Thank you! Your reservation has arrived. We will confirm it shortly.",
      err_prefix: "❌ ",
      net_err:    "❌ Network error — please try again.",
      send_msg:   "Sending message …",
      msg_ok:     "✅ Thank you for your message!",
      msg_err:    "❌ Error while sending.",
    }
  };
  const T = I18N[LANG] || I18N.de;

  // ---------- Reservierung ----------
  const rf = document.getElementById("reservation-form");
  if (rf) rf.addEventListener("submit", async e => {
    e.preventDefault();
    const msg = document.getElementById("res-msg");
    msg.textContent = T.sending; msg.className = "msg";
    const fd = new FormData(rf);
    const payload = Object.fromEntries(fd.entries());
    try {
      const res = await fetch("/api/reservations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.ok) {
        msg.textContent = T.ok;
        msg.className = "msg ok";
        rf.reset();
      } else {
        msg.textContent = T.err_prefix + (data.error || "Fehler");
        msg.className = "msg err";
      }
    } catch (err) {
      msg.textContent = T.net_err;
      msg.className = "msg err";
    }
  });

  // ---------- Kontakt ----------
  const cf = document.getElementById("contact-form");
  if (cf) cf.addEventListener("submit", async e => {
    e.preventDefault();
    const msg = document.getElementById("contact-msg");
    msg.textContent = T.send_msg; msg.className = "msg";
    const fd = new FormData(cf);
    const data = Object.fromEntries(fd.entries());
    const res = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const j = await res.json();
    msg.textContent = j.ok ? T.msg_ok : T.msg_err;
    msg.className = "msg " + (j.ok ? "ok" : "err");
    if (j.ok) cf.reset();
  });

  // ---------- Live Google-Bewertung ----------
  // Wenn das Backend einen Key + Place-ID hat, ersetzt es den Statischen Wert.
  const ratingEl = document.querySelector("[data-google-rating]");
  if (ratingEl) {
    fetch("/api/google-rating")
      .then(r => r.json())
      .then(d => {
        if (d && d.ok && d.rating) {
          ratingEl.textContent = "★ " + d.rating.toFixed(1);
          ratingEl.setAttribute("title", "Live von Google");
        }
      })
      .catch(() => {});
  }
});

// ---------- Scroll-to-top Button ----------
(function () {
  const btn = document.createElement("button");
  btn.className = "scroll-top";
  btn.setAttribute("aria-label", "Scroll to top");
  btn.innerHTML = "↑";
  document.body.appendChild(btn);

  const onScroll = () => {
    if (window.scrollY > 300) btn.classList.add("visible");
    else btn.classList.remove("visible");
  };
  window.addEventListener("scroll", onScroll, { passive: true });

  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  onScroll();
})();
