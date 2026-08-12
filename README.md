# Tbiliso — Первый грузинский ресторан в Ольденбурге (DE / RU)

Веб-сайт ресторана **Tbiliso** (Ammerländer Heerstraße 57, 26129 Oldenburg).
Полностью на немецком и русском. Грузинский удалён из интерфейса (груз. алфавит остался только в названиях блюд как кулинарный стандарт).

## Что сделано

| Задача | Решение |
|---|---|
| 🇬🇪 Грузинский убран | Скопированы все строки в `app.py` (словарь `TRANSLATIONS`) на DE + RU; грузинские маркеры в шаблонах заменены на немецкий/русский |
| 🇷🇺 Переключатель на русский | В шапке кнопки **DE / RU** меняют язык через cookie-сессии |
| 🍽 Меню | Полное меню на двух языках (карта позиций из предыдущей версии + перевод названий и описаний; цены те же) |
| 🔒 Скрытая панель шефа | Кнопка «Admin» в публичной навигации и футере **удалена**, маршрут `/admin` → `/chef` и защищён сессионным логином с паролем. URL входа — **/chef-login** (не виден гостям) |
| 🚀 Публикация | Конфиги `Procfile`, `render.yaml`, `runtime.txt` — деплой одной кнопкой на Render/Railway/Heroku |

## Где смотреть бронирования только шефу

* URL входа: `/chef-login` (НЕ ссылка из меню/футера — знает только владелец)
* Пароль по умолчанию: **TbilisoChef2026!**
  * **Поменяйте** перед продакшеном: переменная окружения `TBILISO_CHEF_PW` или смените строку `CHEF_PASSWORD` в `app.py`
* После входа: `/chef` — список броней и контактных сообщений, смена статусов (`новая → подтв./отказ/завершена`)
* Кнопка «Выйти» — `/chef-logout`
* Сессия 12 часов, httponly cookie.

## Публичные URL

| Слаг | Что показывает |
|---|---|
| `/` | Главная |
| `/ueber-uns` | О нас |
| `/speisekarte` | Полное меню |
| `/reservierung` | Форма бронирования |
| `/kontakt` | Контактная форма |
| `/impressum` | Импрессум |
| `/lang/de`, `/lang/ru` | Переключатель языка |

API: `POST /api/reservations`, `POST /api/contact`.

## Локальный запуск

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## Деплой

### Render.com (бесплатно)
1. Залить содержимое этой папки в Git-репозиторий.
2. На render.com → New → Web Service → подключить репо.
3. Render подхватит `render.yaml` автоматически.
4. Сразу после деплоя: откройте `https://<ваш-домен>/chef-login`, войдите с дефолтным паролем и смените его (`TBILISO_CHEF_PW` в Environment).

### Railway / Heroku
```bash
railway up    # или heroku create && git push heroku main
```

### Любой VPS
```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2
```

## Файлы

```
tbiliso/
├── app.py              ← Flask + i18n + chef-login
├── requirements.txt    ← flask + gunicorn
├── Procfile            ← для Heroku/Render
├── render.yaml
├── runtime.txt         ← версия Python
├── static/
│   ├── css/style.css   ← единый стиль, грузинский шрифт удалён
│   └── js/main.js      ← i18n-сообщения валидации
└── templates/
    ├── base.html       ← шапка с переключателем DE/RU, без admin-ссылки
    ├── index.html
    ├── about.html
    ├── menu.html       ← меню на DE/RU
    ├── reservation.html
    ├── contact.html
    ├── impressum.html
    ├── chef_login.html ← скрытая форма входа
    └── chef_panel.html ← защищённая панель бронирований
```
