// Tbiliso – clientseitige Validierung & Form-Handling (i18n-fähig)
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
    ru: {
      sending:    "Отправляем бронирование…",
      ok:         "✅ Спасибо! Ваша заявка принята. Мы скоро её подтвердим.",
      err_prefix: "❌ ",
      net_err:    "❌ Сетевая ошибка — попробуйте ещё раз.",
      send_msg:   "Отправляем сообщение…",
      msg_ok:     "✅ Спасибо за ваше сообщение!",
      msg_err:    "❌ Ошибка при отправке.",
    }
  };
  const T = I18N[LANG] || I18N.de;

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
});
