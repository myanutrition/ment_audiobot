import logging
import sqlite3
import os
from datetime import datetime, timedelta
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@mya_mentoring"
SEND_HOUR = 7
SEND_MINUTE = 0
ADMIN_CHAT_ID = 7917196527  # твой личный chat_id для уведомлений

# ==================== FILE IDs ====================
VIDEO_NOTE_WELCOME = "DQACAgIAAxkBAAMCalX-QrDwYMp1gwvYzrB1JkpblMMAAv2WAAKX2NBJPUvoedHYVrY9BA"
VIDEO_NOTE_FINAL = "DQACAgIAAxkBAAMDalX-e7AqfuKSReC97Z_Hn3xulegAAiCXAAKX2NBJRNp7aKAhjeg9BA"

AUDIOS = {
    0: "CQACAgIAAxkBAAMFalYCnmw7HXDQviJc8MMK-OnxYD0AAg6qAAJl4bFK0TyaXtVoMbY9BA",
    1: "CQACAgIAAxkBAAMGalYCnuOJZayPZ2ox2M-a2j-jR3UAAhKqAAJl4bFKkrMSlaHmEas9BA",
    2: "CQACAgIAAxkBAAMHalYCnnKL-_NPMAOuZuzLN4R1rDUAAhSqAAJl4bFKvban67A2O3Q9BA",
    3: "CQACAgIAAxkBAAMMalYLd4eVv3QmzI6T3ZmeEHiQ7RIAAn-qAAJl4bFKX6yoRKzX58A9BA",
    4: "CQACAgIAAxkBAAMIalYCnkf5dvXpKGG9XyeAuJuiGowAAhiqAAJl4bFKyUZh7df3WZc9BA",
    5: "CQACAgIAAxkBAAMJalYCngML1RqMI-xo-cJfVVUdtI8AAhuqAAJl4bFKVFi5tuS_8PQ9BA",
    6: "CQACAgIAAxkBAAMKalYCnjGSKjxGxMxcCx3XKbHNd74AAh2qAAJl4bFKHyZmnHKjlqU9BA",
    7: "CQACAgIAAxkBAAMLalYCnj-HpvKp8OYVjpscg2ChalkAAiKqAAJl4bFKT_fJpRNwksc9BA",
}

# ==================== ТЕКСТЫ ====================

TEXT_NOT_SUBSCRIBED = "Чтобы получить доступ к аудиосерии, подпишись на канал автора 🎙️"

TEXT_START_1 = (
    "Привет, коллега! 👋 Я Юля Минченко, нутрициолог с высшим образованием и сертифицированный коуч по питанию 🌿\n\n"
    "Это аудиосериал про 7 главных навыков специалиста по питанию"
)

TEXT_START_2 = (
    "Вас ждёт 7 коротких аудио о том, как в эпоху доступных знаний и искусственного интеллекта быть "
    "востребованным и эффективным специалистом. Чтобы клиенты добивались результатов, а вы наслаждались своей "
    "работой. И, разумеется, чтобы она хорошо оплачивалась 💰\n\n"
    "Эта серия основана на опыте работы с сотнями клиентов и коллег. Приятного прослушивания!"
)

TEXT_START_3 = (
    "Каждый день я буду присылать одно аудио и небольшое задание 📝 Слушайте в комфортном темпе!\n\n"
    "Начинаем с первого навыка! ▶️"
)

TEXTS_BEFORE = {
    1: (
        "*Навык 1. Говорить о своих услугах без страха*\n\n"
        "Сегодня первое аудио про навык, без которого невозможен переход от знаний к практике: как говорить "
        "о своих услугах спокойно, понятно и без ощущения, что вы кому-то навязываетесь.\n\n"
        "Мы разберём, почему фразы вроде «я нутрициолог» или «я помогаю наладить питание» — слишком общие, "
        "и как объяснять свою работу через запросы реальных людей 💡\n\n"
        "Как и зачем говорить про вечерние переедания, усталость от диет, страх сладкого, желание питаться "
        "нормально без подсчётов и постоянного контроля."
    ),
    2: (
        "*Навык 2. Проводить консультацию и не бояться человека напротив*\n\n"
        "Сегодня говорим про консультацию. Пока мы учимся и есть лекции, конспекты и методички, всё кажется "
        "понятным. Но реальный человек, клиент со своим характером, вопросами и ожиданиями может сбить с толку, "
        "а неизвестность будет пугать нас 😰\n\n"
        "В аудио я раскрою формулу встречи с клиентом. Это помогает не теряться и вести разговор "
        "последовательно: запрос, обычный день, главная трудность, первый фокус и действие до следующей встречи."
    ),
    3: (
        "*Навык 3. Слышать клиента до того, чтобы дать совет*\n\n"
        "Сегодня аудио про исправительный рефлекс: как уметь слышать клиента по-настоящему. Когда человек "
        "говорит «я вечером срываюсь на сладкое», за этим может стоять сотни причин 🍫 Это усталость, запреты, "
        "тревога, отсутствие отдыха, страх снова сорваться, ощущение, что сладкое осталось единственным способом "
        "прожить день. Если сразу даёт совет, он может не попасть в настоящую причину, чаще так и происходит."
    ),
    4: (
        "*Навык 4. Объяснять сложное простым языком*\n\n"
        "Сегодня будем говорить о том, как объяснять питание так, чтобы клиенту становилось не труднее, а проще. "
        "В профессии нам хочется спрятаться за терминами: инсулин, грелин, пищевой контроль, энергетический "
        "баланс... 🧬 Но клиенту важно понять, как это относится к его жизни — завтраку, вечернему перееданию, "
        "усталости, сладкому и его обычному дню."
    ),
    5: (
        "*Навык 5. Критически мыслить и разбираться в информации + умело пользоваться ИИ*\n\n"
        "Сегодня аудио про критическое мышление. В теме питания каждый день появляются новые страшилки, "
        "громкие заголовки, посты про вред продуктов, добавки, протоколы, исследования и личные истории 📰 "
        "Специалисту нужен внутренний фильтр, чтобы не повторять чужие выводы автоматически и понимать, откуда "
        "взялось утверждение, кому оно применимо и где у него ограничения."
    ),
    6: (
        "*Навык 6. Работать со сложными клиентскими ситуациями*\n\n"
        "Что делать, если клиент ничего не сделал, пропал, переел, не заполнил дневник, попросил меню, сказал "
        "что всё уже знает, обесценивает и хочет быстрый результат?\n\n"
        "Такие ситуации не делают клиента плохим и не означают, что специалист не справится. Они показывают, "
        "что стоит разобрать внимательнее 🔍"
    ),
    7: (
        "*Навык 7. Собрать свою профессиональную Систему работы*\n\n"
        "Сегодня финальное аудио, где все навыки собираются в вашу Систему. Когда у специалиста нет системы, "
        "каждый новый клиент ощущается как огромный груз, начало с нуля. А каждая консультация — как импровизация, "
        "каждый пищевой дневник — как отдельная головоломка, сложный вопрос воспринимается как проверка на "
        "профессиональность и хорошесть.\n\n"
        "Система помогает понимать, с какими запросами вы работаете, как начинаете консультацию, какие материалы "
        "используете, как даёте задания ✅"
    ),
}

TEXTS_AFTER = {
    1: (
        "После аудио соберите четыре фразы о своей работе ✍️:\n"
        "я помогаю…,\n"
        "ко мне можно прийти, если…,\n"
        "в работе со мной мы будем…,\n"
        "после работы человек сможет….\n\n"
        "Объясняю в аудио!\n\n"
        "Это черновик, который поможет вам самим чётче увидеть ценность своей работы."
    ),
    2: (
        "После аудио возьмите один типичный запрос клиента и разложите его по пяти пунктам:\n"
        "с чем человек пришёл, как выглядит его обычный день, где повторяется главная трудность, какой первый "
        "фокус можно выбрать и какое действие человек попробует до следующей встречи.\n\n"
        "Чтобы отработать свои навыки консультаций на практике, оставляйте заявку в менторство 🌿"
    ),
    3: (
        "После аудио возьмите одну фразу клиента и попробуйте сначала отразить то, что вы услышали 💭\n\n"
        "Например, на фразу «я всё понимаю, но вечером всё равно переедаю» можно ответить: «Похоже, днём вы "
        "правда стараетесь, но к вечеру сил становится настолько мало, что знания уже перестают помогать».\n\n"
        "Так клиент чувствует, что его слышат и помогают разобраться.\n\n"
        "В менторстве вы научитесь навыкам мотивационного консультирования и активного слушания 🌿"
    ),
    4: (
        "После аудио выберите одну сложную тему и объясните её в трёх вариантах: как для коллеги, как для "
        "клиента на консультации и как для короткой сторис.\n\n"
        "Можно взять вечернее переедание, белок, клетчатку, голод и насыщение или тягу к сладкому. Смысл задания "
        "в том, чтобы потренировать перевод с языка учебника на язык реальной жизни ✍️\n\n"
        "В менторстве вы будете сопровождать реального клиента и сможете научиться объяснять важные темы — просто."
    ),
    5: (
        "После аудио возьмите один тезис про питание, который недавно встретили в соцсетях, и проверьте его по "
        "вопросам: кто это сказал, на чём основано утверждение, это мнение, реклама, исследование или личный "
        "опыт, кому это применимо, какие есть ограничения, можно ли использовать это в работе с клиентом и как "
        "объяснить клиенту.\n\n"
        "В менторстве вы сможете разобраться, какие источники читать, как разбирать исследования и использовать "
        "искусственный интеллект в нашей работе 🌿"
    ),
    6: (
        "После аудио выпишите три ситуации, которых вы больше всего боитесь в работе с клиентом, и к каждой "
        "напишите первую фразу специалиста ✍️\n\n"
        "Например, что вы скажете, если клиент просит меню, если клиентка пишет «я сорвалась», если она ничего "
        "не сделала или если говорит, что уже всё знает.\n\n"
        "Задача упражнения — найти конкретную фразу, которая поможет вам сохранить спокойствие, не уйти в "
        "спасательство и не начать стыдить клиента за булочку."
    ),
    7: (
        "Чтобы выстроить свою Систему и наконец начать уверенно работать с клиентами, приглашаю вас в "
        "менторство 🌿\n\n"
        "Группы по 3-4 человека. Сессии каждую неделю. В процессе будете сопровождать реального клиента.\n\n"
        "И за 3 месяца прокачаетесь намного сильнее, чем за годы обучений."
    ),
}

TEXT_FINAL = (
    "Коллега, браво! Вы на одну ступень ближе к тому, чтобы стать самым востребованным специалистом в "
    "сфере питания ⭐\n\n"
    "Спасибо, что прослушали этот аудиосериал 🤍\n\n"
    "Помните.\n\n"
    "Дело не в знаниях. Их сейчас полно.\n"
    "Дело в навыках: умении слышать, упрощать, быть собой. Давать клиентам ощущение, что их понимают, слышат "
    "и хотят помочь.\n\n"
    "Чтобы мы не потерялись, оставляю ссылки 👇"
)

# ==================== КНОПКИ ====================

def kb_subscribe():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/mya_mentoring")],
        [InlineKeyboardButton("✅ Я подписался(ась)", callback_data="check_sub")],
    ])

def kb_interesting():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Интересно! 🌟", callback_data="btn_interesting")],
    ])

def kb_lets_go():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Отлично, давай начнём! ▶️", callback_data="btn_lets_go")],
    ])

def kb_day1():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day1_podcast"], callback_data="day1_podcast")],
        [InlineKeyboardButton(BUTTON_NAMES["day1_mentorship"], callback_data="day1_mentorship")],
    ])

def kb_day2():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day2_podcast"], callback_data="day2_podcast")],
        [InlineKeyboardButton(BUTTON_NAMES["day2_waitlist"], callback_data="day2_waitlist")],
    ])

def kb_day3():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day3_mentorship"], callback_data="day3_mentorship")],
    ])

def kb_day4():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day4_podcast"], callback_data="day4_podcast")],
        [InlineKeyboardButton(BUTTON_NAMES["day4_waitlist"], callback_data="day4_waitlist")],
    ])

def kb_day5():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day5_mentorship"], callback_data="day5_mentorship")],
    ])

def kb_day6():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day6_mentorship"], callback_data="day6_mentorship")],
    ])

def kb_day7():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["day7_podcast"], callback_data="day7_podcast")],
        [InlineKeyboardButton(BUTTON_NAMES["day7_mentorship"], callback_data="day7_mentorship")],
    ])

def kb_final():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_NAMES["final_channel"], callback_data="final_channel")],
        [InlineKeyboardButton(BUTTON_NAMES["final_podcast"], callback_data="final_podcast")],
        [InlineKeyboardButton(BUTTON_NAMES["final_mentorship"], callback_data="final_mentorship")],
        [InlineKeyboardButton(BUTTON_NAMES["final_waitlist"], callback_data="final_waitlist")],
    ])

# URL и подписи для кнопок-ссылок (логируются и открываются через button_handler)
BUTTON_URLS = {
    "day1_podcast": "https://podcast.ru/1855545693",
    "day1_mentorship": "http://myanutrition.ru/mentorstvo",
    "day2_podcast": "https://podcast.ru/e/.dmVD.W0y5u",
    "day2_waitlist": "https://t.me/+Gwu8V5HIfUNmNGY6",
    "day3_mentorship": "http://myanutrition.ru/mentorstvo",
    "day4_podcast": "https://podcast.ru/e/0vaaeTi7R51",
    "day4_waitlist": "https://t.me/+Gwu8V5HIfUNmNGY6",
    "day5_mentorship": "http://myanutrition.ru/mentorstvo",
    "day6_mentorship": "http://myanutrition.ru/mentorstvo",
    "day7_podcast": "https://podcast.ru/1855545693",
    "day7_mentorship": "http://myanutrition.ru/mentorstvo",
    "final_channel": "https://t.me/mya_mentoring",
    "final_podcast": "https://podcast.ru/1855545693",
    "final_mentorship": "http://myanutrition.ru/mentorstvo",
    "final_waitlist": "https://t.me/+Gwu8V5HIfUNmNGY6",
}

BUTTON_NAMES = {
    "day1_podcast": "🎙️ Подкаст «Сам себе нутрициолог pro»",
    "day1_mentorship": "🌿 Подробнее про менторство",
    "day2_podcast": "🎙️ Подкаст «10 самых сложных клиентов»",
    "day2_waitlist": "📋 Лист ожидания в менторство",
    "day3_mentorship": "🌿 Подробнее про менторство",
    "day4_podcast": "🎙️ Подкаст про всестороннее развитие",
    "day4_waitlist": "📋 Лист ожидания в менторство",
    "day5_mentorship": "🌿 Подробнее про менторство",
    "day6_mentorship": "🌿 Подробнее про менторство",
    "day7_podcast": "🎙️ Подкаст «Сам себе нутрициолог pro»",
    "day7_mentorship": "🌿 Подробнее про менторство",
    "final_channel": "💬 Telegram-канал",
    "final_podcast": "🎙️ Подкаст",
    "final_mentorship": "🌿 Групповое менторство",
    "final_waitlist": "📋 Лист ожидания",
}

DAY_KEYBOARDS = {
    1: kb_day1, 2: kb_day2, 3: kb_day3, 4: kb_day4,
    5: kb_day5, 6: kb_day6, 7: kb_day7,
}

# ==================== БАЗА ДАННЫХ ====================

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            start_date TEXT,
            last_day INTEGER DEFAULT 1,
            blocked INTEGER DEFAULT 0,
            subscribed INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            user_id INTEGER,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS button_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            button TEXT,
            user_id INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, start_date, last_day, subscribed) VALUES (?, ?, ?, ?)",
        (user_id, None, 0, 1)
    )
    c.execute(
        "INSERT INTO stats (event, user_id, created_at) VALUES (?, ?, ?)",
        ("new_user", user_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def set_course_started(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    c.execute(
        "UPDATE users SET start_date = ?, last_day = 1 WHERE user_id = ?",
        (today, user_id)
    )
    conn.commit()
    conn.close()

def log_event(event, user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO stats (event, user_id, created_at) VALUES (?, ?, ?)",
        (event, user_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def log_button_click(button, user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO button_clicks (button, user_id, created_at) VALUES (?, ?, ?)",
        (button, user_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def mark_blocked(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT user_id, start_date, last_day FROM users WHERE blocked = 0 AND start_date IS NOT NULL")
    rows = c.fetchall()
    conn.close()
    return rows

def get_users_by_day(day=None):
    """day=None -> все, кто начал курс. day=N -> только те, у кого last_day == N"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    if day is None:
        c.execute("SELECT user_id FROM users WHERE blocked = 0 AND start_date IS NOT NULL")
    else:
        c.execute("SELECT user_id FROM users WHERE blocked = 0 AND last_day = ?", (day,))
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]

def update_last_day(user_id, day):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET last_day = ? WHERE user_id = ?", (day, user_id))
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_stats():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE blocked = 1")
    blocked = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM stats WHERE event = 'not_subscribed'")
    not_subscribed = c.fetchone()[0]

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    c.execute("SELECT COUNT(*) FROM stats WHERE event = 'new_user' AND created_at >= ?", (week_ago,))
    new_week = c.fetchone()[0]

    days_stats = {}
    for day in range(1, 8):
        c.execute("SELECT COUNT(*) FROM users WHERE last_day = ? AND blocked = 0", (day,))
        days_stats[day] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE last_day = 7 AND blocked = 0")
    completed = c.fetchone()[0]

    c.execute("SELECT button, COUNT(*) FROM button_clicks GROUP BY button")
    clicks = dict(c.fetchall())

    conn.close()
    return {
        "total": total,
        "blocked": blocked,
        "not_subscribed": not_subscribed,
        "new_week": new_week,
        "days": days_stats,
        "completed": completed,
        "clicks": clicks,
    }

# ==================== ПРОВЕРКА ПОДПИСКИ ====================

async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# ==================== УВЕДОМЛЕНИЯ АДМИНУ ====================

async def notify_admin(bot, text):
    try:
        await bot.send_message(ADMIN_CHAT_ID, text)
    except Exception as e:
        logging.error(f"Ошибка уведомления админа: {e}")

# ==================== ОТПРАВКА КОНТЕНТА ====================

async def safe_send(bot, user_id, func, *args, **kwargs):
    for attempt in range(3):
        try:
            return await func(user_id, *args, **kwargs)
        except Exception as e:
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                mark_blocked(user_id)
                return None
            if attempt < 2:
                logging.warning(f"Попытка {attempt+1} не удалась для {user_id}: {e}. Повтор через 5 сек...")
                await asyncio.sleep(5)
            else:
                logging.error(f"Все 3 попытки не удались для {user_id}: {e}")
    return None

async def send_welcome(bot, user_id):
    await safe_send(bot, user_id, bot.send_message, TEXT_START_1)
    await asyncio.sleep(1)

    await safe_send(bot, user_id, bot.send_video_note, VIDEO_NOTE_WELCOME)
    await asyncio.sleep(1)

    await safe_send(bot, user_id, bot.send_message, TEXT_START_2, reply_markup=kb_interesting())


async def send_day0_and_day1_start(bot, user_id):
    await safe_send(bot, user_id, bot.send_audio, AUDIOS[0])
    await asyncio.sleep(1)

    await safe_send(bot, user_id, bot.send_message, TEXT_START_3, reply_markup=kb_lets_go())


async def send_day(bot, user_id, day):
    if day > 7:
        return

    await safe_send(bot, user_id, bot.send_message, TEXTS_BEFORE[day], parse_mode="Markdown")
    await asyncio.sleep(1)

    await safe_send(bot, user_id, bot.send_audio, AUDIOS[day])
    await asyncio.sleep(1)

    keyboard = DAY_KEYBOARDS.get(day)
    await safe_send(bot, user_id, bot.send_message, TEXTS_AFTER[day], reply_markup=keyboard() if keyboard else None)

    if day == 7:
        await asyncio.sleep(1)
        await safe_send(bot, user_id, bot.send_video_note, VIDEO_NOTE_FINAL)
        await asyncio.sleep(1)
        await safe_send(bot, user_id, bot.send_message, TEXT_FINAL, reply_markup=kb_final())

    update_last_day(user_id, day)

# ==================== ЕЖЕДНЕВНАЯ ЗАДАЧА ====================

async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    users = get_all_users()
    today = datetime.now().date()

    for user_id, start_date_str, last_day in users:
        if not start_date_str:
            continue
        try:
            start_date = datetime.fromisoformat(start_date_str).date()
            days_passed = (today - start_date).days
            next_day = last_day + 1

            if next_day <= 7 and days_passed == (next_day - 1):
                await send_day(context.bot, user_id, next_day)
                await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"Ошибка в daily_job для пользователя {user_id}: {e}")

# ==================== ХЭНДЛЕРЫ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_exists(user_id):
        await update.message.reply_text("Вы уже зарегистрированы! Ожидайте следующее аудио 🎧")
        return

    subscribed = await is_subscribed(context.bot, user_id)
    if not subscribed:
        log_event("not_subscribed", user_id)
        await update.message.reply_text(TEXT_NOT_SUBSCRIBED, reply_markup=kb_subscribe())
        return

    add_user(user_id)
    username = update.effective_user.username or update.effective_user.first_name
    await notify_admin(context.bot, f"🆕 Новый пользователь: @{username} (ID: {user_id})")
    await send_welcome(context.bot, user_id)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "check_sub":
        subscribed = await is_subscribed(context.bot, user_id)
        if not subscribed:
            await query.message.reply_text(
                "Похоже, вы ещё не подписались 🙈 Подпишитесь на канал и нажмите кнопку снова!",
                reply_markup=kb_subscribe()
            )
            return
        if user_exists(user_id):
            await query.message.reply_text("Вы уже зарегистрированы! Ожидайте следующее аудио 🎧")
            return
        add_user(user_id)
        username = query.from_user.username or query.from_user.first_name
        await notify_admin(context.bot, f"🆕 Новый пользователь: @{username} (ID: {user_id})")
        await query.message.reply_text("Отлично, подписка подтверждена! 🎉 Начинаем!")
        await send_welcome(context.bot, user_id)
        return

    if data == "btn_interesting":
        log_button_click("btn_interesting", user_id)
        await send_day0_and_day1_start(context.bot, user_id)
        return

    if data == "btn_lets_go":
        log_button_click("btn_lets_go", user_id)
        set_course_started(user_id)
        await send_day(context.bot, user_id, 1)
        return

    if data in BUTTON_URLS:
        log_button_click(data, user_id)
        url = BUTTON_URLS[data]
        name = BUTTON_NAMES[data]
        await query.message.reply_text(
            "Переходи по ссылке 👇",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(name, url=url)]])
        )
        return


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    s = get_stats()

    days_text = ""
    for day, count in s["days"].items():
        days_text += f"  День {day}: {count} чел.\n"

    clicks_text = ""
    for btn, count in s["clicks"].items():
        name = BUTTON_NAMES.get(btn, btn)
        clicks_text += f"  {name}: {count}\n"

    if not clicks_text:
        clicks_text = "  Пока нет кликов\n"

    text = (
        f"📊 Статистика бота\n\n"
        f"👥 Всего пользователей: {s['total']}\n"
        f"🆕 Новых за неделю: {s['new_week']}\n"
        f"🚫 Заблокировали бота: {s['blocked']}\n"
        f"❌ Не подписались и ушли: {s['not_subscribed']}\n"
        f"✅ Завершили серию (День 7): {s['completed']}\n\n"
        f"📅 По дням:\n{days_text}\n"
        f"🔘 Клики по кнопкам:\n{clicks_text}"
    )

    await update.message.reply_text(text)


async def fixdb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    c.execute("SELECT user_id, start_date FROM users")
    rows = c.fetchall()
    fixed = 0
    for user_id, start_date in rows:
        if start_date and (len(str(start_date)) != 10 or not str(start_date).startswith('20')):
            c.execute("UPDATE users SET start_date = ? WHERE user_id = ?", (today, user_id))
            fixed += 1
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Исправлено записей: {fixed}\nУстановлена дата: {today}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальная рассылка с картинкой.
    /broadcast all
    /broadcast day 3
    Ответом на фото с подписью — разошлёт фото+текст. Просто текстом после команды — только текст.
    """
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Использование:\n"
            "/broadcast all — всем\n"
            "/broadcast day 3 — только тем, кто на дне 3\n\n"
            "Отправьте команду в ответ на фото с подписью — разошлём фото+текст.\n"
            "Или просто текстом после команды — разошлём только текст."
        )
        return

    target = args[0].lower()
    day = None
    text_start_index = 1

    if target == "day":
        if len(args) < 2 or not args[1].isdigit():
            await update.message.reply_text("Укажите день числом: /broadcast day 3")
            return
        day = int(args[1])
        text_start_index = 2
    elif target != "all":
        await update.message.reply_text("Первый аргумент должен быть 'all' или 'day'.")
        return

    photo_file_id = None
    caption = None

    replied = update.message.reply_to_message
    if replied and replied.photo:
        photo_file_id = replied.photo[-1].file_id
        caption = replied.caption
    else:
        manual_text = " ".join(args[text_start_index:])
        caption = manual_text or None

    if not caption and not photo_file_id:
        await update.message.reply_text(
            "Не нашёл ни текста, ни фото для рассылки.\n"
            "Либо ответьте командой на сообщение с фото+подписью,\n"
            "либо напишите текст после команды."
        )
        return

    users = get_users_by_day(day)
    label = "всем" if day is None else f"тем, кто на дне {day}"
    await update.message.reply_text(f"🚀 Начинаю рассылку ({label}): {len(users)} чел...")

    sent, failed = 0, 0
    for user_id in users:
        try:
            if photo_file_id:
                await context.bot.send_photo(user_id, photo_file_id, caption=caption, parse_mode="HTML")
            else:
                await context.bot.send_message(user_id, caption, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                mark_blocked(user_id)
            failed += 1
            logging.error(f"Ошибка рассылки для {user_id}: {e}")

    await update.message.reply_text(f"✅ Рассылка завершена!\nОтправлено: {sent}\nОшибок: {failed}")


async def runnow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    await update.message.reply_text("🚀 Запускаю рассылку прямо сейчас...")
    await daily_job(context)
    await update.message.reply_text("✅ Рассылка завершена!")


async def test_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    user_id = update.effective_user.id
    await update.message.reply_text("🧪 Запускаю тестовый режим...")

    await send_welcome(context.bot, user_id)
    await asyncio.sleep(2)
    await send_day0_and_day1_start(context.bot, user_id)

    for day in range(1, 8):
        await asyncio.sleep(2)
        await send_day(context.bot, user_id, day)

    await update.message.reply_text("✅ Тест завершён!")

# ==================== ЗАПУСК ====================

def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_mode))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("runnow", runnow_command))
    app.add_handler(CommandHandler("fixdb", fixdb_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    job_queue = app.job_queue
    now = datetime.now()
    target_time = now.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0)
    if now >= target_time:
        target_time += timedelta(days=1)
    delay = (target_time - now).total_seconds()
    job_queue.run_repeating(daily_job, interval=86400, first=delay)

    print("Бот запущен! ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
