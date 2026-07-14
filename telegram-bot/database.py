import aiosqlite
import random
import string
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT,
            card TEXT DEFAULT '', crypto TEXT DEFAULT '', wallet TEXT DEFAULT '',
            referrer_id INTEGER DEFAULT NULL,
            bal_stars REAL DEFAULT 0, bal_usdt REAL DEFAULT 0, bal_ton REAL DEFAULT 0,
            bal_rub   REAL DEFAULT 0, bal_byn  REAL DEFAULT 0, bal_kzt REAL DEFAULT 0,
            bal_uzs   REAL DEFAULT 0,
            stars_username TEXT DEFAULT '',
            lang TEXT DEFAULT 'ru')""")
        await db.execute("""CREATE TABLE IF NOT EXISTS deals (
            id TEXT PRIMARY KEY, creator_id INTEGER NOT NULL, creator_role TEXT NOT NULL,
            buyer_id INTEGER DEFAULT NULL, seller_id INTEGER DEFAULT NULL,
            amount REAL NOT NULL, currency TEXT NOT NULL, description TEXT NOT NULL,
            status TEXT DEFAULT 'pending')""")
        await db.execute("""CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            currency TEXT NOT NULL, amount REAL NOT NULL, requisite TEXT NOT NULL,
            status TEXT DEFAULT 'pending')""")
        # Migration: add UAH balance column for bots created before UAH support existed.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN bal_uah REAL DEFAULT 0")
        except Exception:
            pass
        # Migration: add lang column for bots created before the language
        # switcher existed.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'ru'")
        except Exception:
            pass
        await db.commit()


async def register_user(user_id, username, referrer_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id FROM users WHERE id=?", (user_id,))
        if not await cur.fetchone():
            await db.execute("INSERT INTO users (id,username,referrer_id) VALUES (?,?,?)",
                             (user_id, username or "", referrer_id))
            await db.commit()
            return True
        return False


async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return await cur.fetchone()


async def update_username(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET username=? WHERE id=?", (username or "", user_id))
        await db.commit()


async def get_lang(user_id) -> str:
    user = await get_user(user_id)
    lang = user["lang"] if user and "lang" in user.keys() else None
    return lang if lang in ("ru", "en") else "ru"


async def set_lang(user_id, lang: str):
    if lang not in ("ru", "en"):
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang=? WHERE id=?", (lang, user_id))
        await db.commit()


async def has_requisites(user_id):
    user = await get_user(user_id)
    if not user:
        return False
    return any(bool((user[f] or '').strip()) for f in ('card', 'crypto', 'wallet'))


async def update_requisite(user_id, field, value):
    if field not in {"card", "crypto", "wallet", "stars_username"}:
        raise ValueError
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field}=? WHERE id=?", (value, user_id))
        await db.commit()


async def _gen_deal_id():
    while True:
        did = ''.join(random.choices(string.digits, k=8))
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT id FROM deals WHERE id=?", (did,))
            if not await cur.fetchone():
                return did


async def create_deal(creator_id, creator_role, amount, currency, description):
    did = await _gen_deal_id()
    buyer_id  = creator_id if creator_role == "buyer"  else None
    seller_id = creator_id if creator_role == "seller" else None
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO deals (id,creator_id,creator_role,buyer_id,seller_id,amount,currency,description,status)"
            " VALUES (?,?,?,?,?,?,?,?,'pending')",
            (did, creator_id, creator_role, buyer_id, seller_id, amount, currency, description))
        await db.commit()
    return did


async def get_deal(deal_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM deals WHERE id=?", (deal_id,))
        return await cur.fetchone()


async def set_deal_buyer(deal_id, buyer_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE deals SET buyer_id=? WHERE id=?", (buyer_id, deal_id))
        await db.commit()


async def update_deal_status(deal_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE deals SET status=? WHERE id=?", (status, deal_id))
        await db.commit()


CURRENCY_FIELDS = {
    "Stars": "bal_stars", "USDT": "bal_usdt", "TON": "bal_ton",
    "RUB":   "bal_rub",   "BYN":  "bal_byn",  "KZT": "bal_kzt",
    "UZS":   "bal_uzs",   "UAH":  "bal_uah",
}

# Maps any lowercase spelling/alias a user might type to the canonical
# currency code used in CURRENCY_FIELDS. Lets people type usdt, USDT, Usdt,
# ton, TON, руб, РУБ, грн, uah, uan, etc. and still hit the right currency.
CURRENCY_ALIASES = {
    "stars": "Stars", "star": "Stars", "старс": "Stars", "звезды": "Stars", "звёзды": "Stars",
    "usdt": "USDT", "tether": "USDT",
    "ton": "TON", "тон": "TON",
    "rub": "RUB", "rur": "RUB", "руб": "RUB", "рубль": "RUB", "рублей": "RUB", "рубли": "RUB",
    "byn": "BYN", "бел": "BYN", "белрубль": "BYN",
    "kzt": "KZT", "тенге": "KZT",
    "uzs": "UZS", "сум": "UZS", "сумы": "UZS",
    "uah": "UAH", "uan": "UAH", "грн": "UAH", "грн.": "UAH", "гривна": "UAH", "гривны": "UAH", "гривен": "UAH",
}


def normalize_currency(raw: str) -> str | None:
    """Case/alias-insensitive currency lookup. Returns the canonical code
    used in CURRENCY_FIELDS, or None if it isn't recognized."""
    if not raw:
        return None
    key = raw.strip().lower()
    if key in CURRENCY_ALIASES:
        return CURRENCY_ALIASES[key]
    for code in CURRENCY_FIELDS:
        if code.lower() == key:
            return code
    return None


async def credit_balance(user_id, currency, amount):
    field = CURRENCY_FIELDS.get(currency)
    if not field:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field}={field}+? WHERE id=?", (amount, user_id))
        await db.commit()


async def debit_balance(user_id, currency, amount):
    field = CURRENCY_FIELDS.get(currency)
    if not field:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(f"SELECT {field} FROM users WHERE id=?", (user_id,))
        row = await cur.fetchone()
        if not row or row[0] < amount:
            return False
        await db.execute(f"UPDATE users SET {field}={field}-? WHERE id=?", (amount, user_id))
        await db.commit()
        return True


async def count_referrals(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0


async def create_withdrawal(user_id, currency, amount, requisite):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO withdrawals (user_id,currency,amount,requisite,status) VALUES (?,?,?,?,'pending')",
            (user_id, currency, amount, requisite))
        await db.commit()
        return cur.lastrowid


async def get_withdrawal(withdraw_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM withdrawals WHERE id=?", (withdraw_id,))
        return await cur.fetchone()


async def update_withdrawal_status(withdraw_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE withdrawals SET status=? WHERE id=?", (status, withdraw_id))
        await db.commit()


async def find_user_by_username(username):
    username = username.lstrip("@")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username,))
        return await cur.fetchone()
