"""
Tbiliso — Первый грузинский ресторан в Ольденбурге
Flask backend с SQLite-базой для бронирования столиков + i18n (DE/RU)
и защищённым /chef-pаschwort раздел только для владельца.
"""
import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for,
    abort, flash, session, make_response,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tbiliso.db")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("TBILISO_SECRET", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 12,  # 12 ч
)

# ---------- Пароль шефа (защита /chef) ----------
# ВАЖНО: поменяйте значение через переменную окружения TBILISO_CHEF_PW
# или отредактируйте строку ниже. Передайте пароль только шефу!
CHEF_PASSWORD = os.environ.get("TBILISO_CHEF_PW", "TbilisoChef2026!")

# ---------- База данных ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            email        TEXT    NOT NULL,
            phone        TEXT    NOT NULL,
            date         TEXT    NOT NULL,
            time         TEXT    NOT NULL,
            guests       INTEGER NOT NULL,
            occasion     TEXT,
            notes        TEXT,
            status       TEXT    NOT NULL DEFAULT 'neu',
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            email   TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    init_db()

# ---------- i18n: DE + RU (грузинский удалён) ----------
LANGS = ("de", "ru")
DEFAULT_LANG = "de"

TRANSLATIONS = {
    "de": {
        # header / nav
        "nav_home":     "Start",
        "nav_about":    "Über uns",
        "nav_menu":     "Speisekarte",
        "nav_res":      "Reservierung",
        "nav_contact":  "Kontakt",
        "cta_reserve":  "Tisch reservieren",
        # başlıklar
        "tagline":      "Erstes georgisches Restaurant in Oldenburg",
        "subtitle":     "Authentische georgische Küche · Wein · Supra",
        "kicker":       "Tbilissi · Oldenburg · seit 2025",
        "hero_title_1": "Tbiliso — das erste",
        "hero_title_2": "georgische Restaurant",
        "hero_title_3": "in Oldenburg",
        "hero_lead":    ("Willkommen zu einer kulinarischen Reise ins Herz Georgiens. "
                         "Authentische Chatschapuri, handgedrehte Chinkali, sanft geschmortes "
                         "Chakapuli und georgischer Wein aus uralter Qvevri-Tradition — "
                         "serviert mit der berühmten georgischen Gastfreundschaft."),
        "cta_wolt":     "Lieferung über Wolt",
        "section_dishes_h":  "Kulinarische Reise nach Georgien",
        "section_dishes_p":  "Eine Auswahl unserer beliebtesten Gerichte — alles hausgemacht nach Originalrezepten.",
        "see_full_menu":     "Vollständige Speisekarte ansehen",
        "supra_h":     "Supra — die georgische Tafel",
        "supra_p_1":   ("In Georgien bedeutet Essen Gemeinschaft. Eine Supra ist mehr als ein Tisch — "
                        "es ist ein Ritual aus Brot, Wein, Geschichten und Gesang."),
        "supra_p_2":   "Bei Tbiliso laden wir Sie ein, genau diese Wärme zu erleben.",
        "feature_1":   "Hausgemachte Chatschapuri & Chinkali",
        "feature_2":   "Georgische Weine aus regionalen Winzern",
        "feature_3":   "Vegane & vegetarische Gerichte",
        "feature_4":   "Catering für Hochzeiten, Geburtstage & Firmenfeiern",
        "reserve_now": "Jetzt Tisch reservieren",
        "cta_h":       "Reservieren Sie Ihren Abend bei Tbiliso",
        "cta_p":       "Wir freuen uns auf Sie — direkt online oder telefonisch.",
        # meta & dishes
        "dish_1_h":    "Chatschapuri Adscharuli",
        "dish_1_p":    "Das berühmte schwimmende Käse-Boot mit Sulguni & Imeruli, gekrönt von einem rohen Eigelb und einem Stück Butter.",
        "dish_2_h":    "Chinkali",
        "dish_2_p":    "Handgedrehte Teigtaschen mit Rind-Suppe & Kräutern, kunstvoll am Knopf gegessen. Mindestens 3 Stück pro Person.",
        "dish_3_h":    "Qvevri-Wein",
        "dish_3_p":    "Amber- oder Saperavi aus 8000-jähriger Qvevri-Tradition — aus der Erde fermentiert, von der Sonne gereift.",
        "dish_4_h":    "Satsivi",
        "dish_4_p":    "Hähnchen in würziger Walnuss-Sauce mit Knoblauch und georgischen Gewürzen — kalt serviert.",
        # kontakt / adres
        "address_h":   "Adresse",
        "hours_h":     "Öffnungszeiten",
        "delivery_h":  "Lieferung & Social",
        "meta_rating":         "★ Google-Bewertung",
        "meta_first_georgian": "1. georgisches Restaurant in Oldenburg",
        "meta_wine_tradition": "Jahre Wein-Tradition",
        # about
        "about_h_1":   "Über uns",
        "about_p_li_1": "Das erste georgische Restaurant in Oldenburg",
        "about_p_li_2": "Authentische Rezepte, frische Produkte, hausgemacht",
        "about_p_li_3": "Vegane und vegetarische Gerichte",
        "about_p_li_4": "Qvevri-Weine nach uralter Tradition",
        "about_p_li_5": "Catering für Hochzeiten & Firmenfeiern",
        # kontakt form
        "form_name":  "Name *",
        "form_email": "E-Mail *",
        "form_msg":   "Nachricht *",
        "form_send":  "Senden",
        # reservierung form
        "form_phone": "Telefon *",
        "form_occasion": "Anlass (optional)",
        "form_date":  "Datum *",
        "form_time":  "Uhrzeit *",
        "form_guests":"Gäste *",
        "form_notes": "Besondere Wünsche",
        "form_submit":"Reservierung absenden",
        # impressum / haftung
        "impressum_h":"Impressum",
        "impressum_legal_hint": "Dieses Impressum ist ein Platzhalter. Vor Veröffentlichung bitte von einem Anwalt prüfen lassen.",
        # speisekarte headline
        "menu_h":    "Speisekarte",
        "menu_p":    "Alle Gerichte hausgemacht, frisch zubereitet nach Originalrezepten aus Georgien.",
        # мenu section headlines
        "m_chatsch": "Chatschapuri",
        "m_chink":   "Chinkali",
        "m_main":    "Hauptgerichte",
        "m_salads":  "Salate & Vorspeisen",
        "m_wine":    "Weine (Qvevri)",
        "m_dessert": "Desserts",
        "m_prices_hint": "⚠ Preise sind Richtwerte und können saisonal variieren. Aktuelle Preise auf Anfrage.",
        # Резервация сообщения
        "res_send_ok": "✅ Vielen Dank! Ihre Reservierung ist eingegangen. Wir bestätigen sie in Kürze.",
        "res_send_err": "❌ ",
    },
    "ru": {
        "nav_home":     "Главная",
        "nav_about":    "О нас",
        "nav_menu":     "Меню",
        "nav_res":      "Бронирование",
        "nav_contact":  "Контакты",
        "cta_reserve":  "Забронировать столик",
        "tagline":      "Первый грузинский ресторан в Ольденбурге",
        "subtitle":     "Аутентичная грузинская кухня · Вино · Супра",
        "kicker":       "Тбилиси · Ольденбург · с 2025",
        "hero_title_1": "Tbiliso — первый",
        "hero_title_2": "грузинский ресторан",
        "hero_title_3": "в Ольденбурге",
        "hero_lead":    ("Добро пожаловать в кулинарное путешествие в сердце Грузии. "
                         "Настоящие хачапури, ручной работы хинкали, нежное чакопули "
                         "и грузинское вино из древней Qvevri-традиции — "
                         "всё это подаётся с легендарным грузинским гостеприимством."),
        "cta_wolt":     "Доставка через Wolt",
        "section_dishes_h":  "Кулинарное путешествие в Грузию",
        "section_dishes_p":  "Подборка наших самых популярных блюд — всё домашнее, по оригинальным рецептам.",
        "see_full_menu":     "Посмотреть полное меню",
        "supra_h":     "Супра — грузинское застолье",
        "supra_p_1":   ("В Грузии еда — это общение. Супра — это не просто стол, "
                        "а целый ритуал: хлеб, вино, истории и песни."),
        "supra_p_2":   "В Tbiliso мы приглашаем вас ощутить именно это тепло.",
        "feature_1":   "Домашние хачапури и хинкали",
        "feature_2":   "Грузинские вина от местных виноделов",
        "feature_3":   "Веганские и вегетарианские блюда",
        "feature_4":   "Кейтеринг для свадеб, дней рождения и корпоративов",
        "reserve_now": "Забронировать столик",
        "cta_h":       "Забронируйте свой вечер в Tbiliso",
        "cta_p":       "Будем рады вас видеть — онлайн или по телефону.",
        "dish_1_h":    "Хачапури по-аджарски",
        "dish_1_p":    "Знаменитая «лодочка» с сыром сулгуни и имеретинским, увенчанная сырым желтком и кусочком масла.",
        "dish_2_h":    "Хинкали",
        "dish_2_p":    "Ручные пельмени с говяжьим бульоном и травами; едят за хвостик. Минимум 3 шт. на человека.",
        "dish_3_h":    "Вино из квеври",
        "dish_3_p":    "Янтарное или Саперави по 8000-летней традиции Qvevri — брожение в земле, созревание на солнце.",
        "dish_4_h":    "Сациви",
        "dish_4_p":    "Курица в пряном ореховом соусе с чесноком и грузинскими специями — подаётся холодной.",
        "address_h":   "Адрес",
        "hours_h":     "Часы работы",
        "delivery_h":  "Доставка и соцсети",
        "meta_rating":         "★ рейтинг Google",
        "meta_first_georgian": "1-й грузинский ресторан в Ольденбурге",
        "meta_wine_tradition": "лет винодельческой традиции",
        "about_h_1":   "О нас",
        "about_p_li_1": "Первый грузинский ресторан в Ольденбурге",
        "about_p_li_2": "Аутентичные рецепты, свежие продукты, всё домашнее",
        "about_p_li_3": "Веганские и вегетарианские блюда",
        "about_p_li_4": "Вина Qvevri по древней традиции",
        "about_p_li_5": "Кейтеринг для свадеб и корпоративов",
        "form_name":  "Имя *",
        "form_email": "E-mail *",
        "form_msg":   "Сообщение *",
        "form_send":  "Отправить",
        "form_phone": "Телефон *",
        "form_occasion": "Повод (необязательно)",
        "form_date":  "Дата *",
        "form_time":  "Время *",
        "form_guests":"Гости *",
        "form_notes": "Особые пожелания",
        "form_submit":"Отправить бронирование",
        "impressum_h":"Импрессум",
        "impressum_legal_hint": "Этот импрессум — шаблон. Перед публикацией необходимо проверить у юриста.",
        "menu_h":    "Меню",
        "menu_p":    "Все блюда готовятся дома, по оригинальным рецептам из Грузии.",
        "m_chatsch": "Хачапури",
        "m_chink":   "Хинкали",
        "m_main":    "Основные блюда",
        "m_salads":  "Салаты и закуски",
        "m_wine":    "Вина (квеври)",
        "m_dessert": "Десерты",
        "m_prices_hint": "⚠ Цены ориентировочные и могут меняться в зависимости от сезона. Актуальные цены — по запросу.",
        "res_send_ok": "✅ Спасибо! Ваша бронь принята. Мы скоро её подтвердим.",
        "res_send_err": "❌ ",
    }
}

# ---------- Утилиты локализации ----------
def get_lang():
    lang = session.get("lang")
    if lang in LANGS:
        return lang
    # fallback на лучшую поддерживаемую по Accept-Language
    best = request.accept_languages.best_match(LANGS)
    return best if best in LANGS else DEFAULT_LANG

def t(key):
    return TRANSLATIONS[get_lang()].get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))

@app.context_processor
def inject_i18n():
    return {"t": t, "lang": get_lang(), "LANGS": LANGS}

@app.route("/lang/<code>")
def set_lang(code):
    if code in LANGS:
        session["lang"] = code
        # если есть параметр ?next=… вернёмся туда
        nxt = request.args.get("next")
        if nxt and nxt.startswith("/"):
            return redirect(nxt)
    return redirect(request.referrer or url_for("index"))

# ---------- Константы ----------
RESTAURANT = {
    "name": "Tbiliso",
    "address": "Ammerländer Heerstraße 57, 26129 Oldenburg",
    "phone": "+49 1522 8731956",
    "phone_display": "01522 8731956",
    "owner": "Zurab Zibzibadze",
    "email": "kontakt@tbiliso-oldenburg.de",
    "rating": 3.9,
    "rating_source": "Google Maps",
    "wolt_url": "https://wolt.com/en/deu/oldenburg",
    "hours": [
        ("Mo – Do", "12:00 – 22:00"),
        ("Fr – Sa", "12:00 – 23:30"),
        ("So",      "13:00 – 22:00"),
    ],
    # понедельник–четверг RU-вариант
    "hours_ru": [
        ("Пн – Чт", "12:00 – 22:00"),
        ("Пт – Сб", "12:00 – 23:30"),
        ("Вс",      "13:00 – 22:00"),
    ],
}

def hours_for_lang():
    return RESTAURANT["hours_ru"] if get_lang() == "ru" else RESTAURANT["hours"]

@app.context_processor
def inject_restaurant():
    r = dict(RESTAURANT)
    r["hours"] = hours_for_lang()
    return {"r": r}

# ---------- Публичные маршруты ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speisekarte")
def menu():
    return render_template("menu.html")

@app.route("/reservierung")
def reservation_page():
    return render_template("reservation.html")

@app.route("/kontakt")
def contact():
    return render_template("contact.html")

@app.route("/ueber-uns")
def about():
    return render_template("about.html")

@app.route("/impressum")
def impressum():
    return render_template("impressum.html")

# ---------- API: бронирование ----------
@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    data = request.get_json(silent=True) or request.form
    required = ["name", "email", "phone", "date", "time", "guests"]
    missing = [f for f in required if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"ok": False, "error": "Pflichtfelder fehlen"}), 400
    try:
        d = datetime.strptime(data["date"], "%Y-%m-%d")
        t = datetime.strptime(data["time"], "%H:%M")
        guests = int(data["guests"])
    except ValueError:
        return jsonify({"ok": False, "error": "Ungültige Eingabe"}), 400
    if guests < 1 or guests > 20:
        return jsonify({"ok": False, "error": "Gästeanzahl 1–20"}), 400
    if d.date() < datetime.now().date():
        return jsonify({"ok": False, "error": "Datum liegt in der Vergangenheit"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reservations (name, email, phone, date, time, guests, occasion, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"].strip(), data["email"].strip(), data["phone"].strip(),
        data["date"].strip(), data["time"].strip(), guests,
        (data.get("occasion") or "").strip(), (data.get("notes") or "").strip(),
    ))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "id": new_id})

@app.route("/api/contact", methods=["POST"])
def contact_message():
    data = request.get_json(silent=True) or request.form
    missing = [f for f in ["name", "email", "message"] if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"ok": False, "error": "Pflichtfelder fehlen"}), 400
    conn = get_db()
    conn.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
                 (data["name"].strip(), data["email"].strip(), data["message"].strip()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ---------- Защита раздела шефа ----------
def chef_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_chef"):
            # Скрытый URL — обычные посетители даже не знают, что он существует.
            return redirect(url_for("chef_login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/chef-login", methods=["GET", "POST"])
def chef_login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if secrets.compare_digest(pw, CHEF_PASSWORD):
            session["is_chef"] = True
            session.permanent = False
            return redirect(url_for("chef_panel"))
        flash({"ru": "Неверный пароль.", "de": "Falsches Passwort."}[get_lang()])
    return render_template("chef_login.html")

@app.route("/chef-logout")
def chef_logout():
    session.pop("is_chef", None)
    return redirect(url_for("index"))

# ЭТО И ЕСТЬ «кнопка админ», которую видит только шеф после входа.
@app.route("/chef")
@chef_required
def chef_panel():
    conn = get_db()
    rows = conn.execute("SELECT * FROM reservations ORDER BY created_at DESC").fetchall()
    contacts = conn.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("chef_panel.html",
                           reservations=rows, contacts=contacts)

@app.route("/chef/reservation/<int:rid>/status", methods=["POST"])
@chef_required
def set_status(rid):
    new = request.form.get("status", "neu")
    if new not in ("neu", "bestaetigt", "abgelehnt", "abgeschlossen"):
        abort(400)
    conn = get_db()
    conn.execute("UPDATE reservations SET status=? WHERE id=?", (new, rid))
    conn.commit()
    conn.close()
    flash({
        "de": f"Status der Reservierung #{rid} → '{new}'.",
        "ru": f"Статус бронирования #{rid} → '{new}'.",
    }[get_lang()])
    return redirect(url_for("chef_panel"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
