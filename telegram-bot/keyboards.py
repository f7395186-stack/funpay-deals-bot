from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FUNPAY_URL

# NOTE ON PREMIUM EMOJI: the Telegram Bot API only allows *plain text* on
# InlineKeyboardButton labels -- custom/premium animated emoji (the
# <tg-emoji> entities used throughout the message texts in emojis.py) cannot
# be rendered inside button labels, regardless of whether the bot owner has
# Telegram Premium. This is a hard platform limitation, not a bug here.
# Buttons below use regular unicode emoji, which is the maximum Telegram
# currently supports for button labels.


def btn(text: str, callback: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback)


def btn_url(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))


def back_row():
    return [btn("🏠 Главное меню", "main_menu")]


def back_kb() -> InlineKeyboardMarkup:
    return kb(back_row())


def main_menu_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("🤝 Создать сделку", "create_deal"),  btn("💰 Баланс", "balance")],
        [btn("👛 Реквизиты", "requisites"),          btn("🎁 Рефералы", "referrals")],
        [btn("💎 F.A.Q", "faq"),                     btn_url("🌐 WEB маркет", FUNPAY_URL)],
        [btn("⚡ Поддержка", "support")],
    )


def deal_role_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("🛒 Я — Покупатель", "role_buyer"), btn("💼 Я — Продавец", "role_seller")],
        back_row(),
    )


def currency_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("⭐ Stars",  "cur_Stars"), btn("💵 USDT", "cur_USDT")],
        [btn("💎 TON",   "cur_TON"),   btn("🇷🇺 RUB",  "cur_RUB")],
        [btn("🇧🇾 BYN",  "cur_BYN"),  btn("🇰🇿 KZT",  "cur_KZT")],
        [btn("🇺🇿 UZS",  "cur_UZS"),  btn("🇺🇦 UAH",  "cur_UAH")],
        back_row(),
    )


def cancel_kb() -> InlineKeyboardMarkup:
    return kb([btn("❌ Отмена", "main_menu")])


def attach_req_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("👛 Привязать реквизиты", "requisites")],
        [btn("🤝 Создать сделку", "create_deal")],
        back_row(),
    )


def pay_deal_kb(deal_id: str) -> InlineKeyboardMarkup:
    return kb(
        [btn("💳 Оплатить сделку", f"pay_deal_{deal_id}")],
        back_row(),
    )


def confirm_kb(deal_id: str) -> InlineKeyboardMarkup:
    return kb(
        [btn("✅ Подтвердить получение товара", f"confirm_deal_{deal_id}")],
        back_row(),
    )


def balance_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("➕ Пополнить", "deposit"), btn("💸 Вывести", "withdraw")],
        back_row(),
    )


def withdraw_currency_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("⭐ Stars",  "wcur_Stars"), btn("💵 USDT", "wcur_USDT")],
        [btn("💎 TON",   "wcur_TON"),   btn("🇷🇺 RUB",  "wcur_RUB")],
        [btn("🇧🇾 BYN",  "wcur_BYN"),  btn("🇰🇿 KZT",  "wcur_KZT")],
        [btn("🇺🇿 UZS",  "wcur_UZS"),  btn("🇺🇦 UAH",  "wcur_UAH")],
        back_row(),
    )


def requisites_kb() -> InlineKeyboardMarkup:
    return kb(
        [btn("💳 Изменить карту",      "edit_card")],
        [btn("🪙 Изменить крипту",     "edit_crypto")],
        [btn("👛 Изменить кошелёк",    "edit_wallet")],
        [btn("⭐ Юзернейм для Stars",  "edit_stars")],
        [btn("🤝 Создать сделку",      "create_deal")],
        back_row(),
    )


def referrals_kb(ref_link: str) -> InlineKeyboardMarkup:
    return kb(
        [btn_url("📤 Поделиться ссылкой", f"https://t.me/share/url?url={ref_link}")],
        back_row(),
    )


def withdraw_review_kb(withdraw_id: int) -> InlineKeyboardMarkup:
    return kb([
        btn("✅ Выполнено", f"wd_done_{withdraw_id}"),
        btn("❌ Отклонить", f"wd_reject_{withdraw_id}"),
    ])
