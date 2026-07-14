from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FUNPAY_URL
from i18n import b

# NOTE ON PREMIUM EMOJI: the Telegram Bot API only allows *plain text* on
# InlineKeyboardButton labels -- custom/premium animated emoji (the
# <tg-emoji> entities used throughout the message texts in emojis.py) cannot
# be rendered inside button labels, regardless of whether the bot owner has
# Telegram Premium. This is a hard platform limitation, not a bug here.
# Buttons below use regular unicode emoji, which is the maximum Telegram
# currently supports for button labels.
#
# NOTE ON LANGUAGE: every keyboard function below takes a `lang` argument
# ("ru" or "en") so button labels render in the acting user's chosen
# language. Always pass the user's own stored language (db.get_lang), not a
# hardcoded default.


def btn(text: str, callback: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback)


def btn_url(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))


def back_row(lang: str = "ru"):
    return [btn(b(lang, "main_menu"), "main_menu")]


def back_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(back_row(lang))


def main_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "create_deal"), "create_deal"), btn(b(lang, "balance"), "balance")],
        [btn(b(lang, "requisites"),  "requisites"),  btn(b(lang, "referrals"), "referrals")],
        [btn(b(lang, "faq"),         "faq"),         btn_url(b(lang, "web_market"), FUNPAY_URL)],
        [btn(b(lang, "support"),     "support")],
        [btn(b(lang, "language"),    "lang_menu")],
    )


def deal_role_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "role_buyer"), "role_buyer"), btn(b(lang, "role_seller"), "role_seller")],
        back_row(lang),
    )


def currency_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn("⭐ Stars",  "cur_Stars"), btn("💵 USDT", "cur_USDT")],
        [btn("💎 TON",   "cur_TON"),   btn("🇷🇺 RUB",  "cur_RUB")],
        [btn("🇧🇾 BYN",  "cur_BYN"),  btn("🇰🇿 KZT",  "cur_KZT")],
        [btn("🇺🇿 UZS",  "cur_UZS"),  btn("🇺🇦 UAH",  "cur_UAH")],
        back_row(lang),
    )


def cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb([btn(b(lang, "cancel"), "main_menu")])


def attach_req_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "link_requisites"), "requisites")],
        [btn(b(lang, "create_deal"),     "create_deal")],
        back_row(lang),
    )


def pay_deal_kb(deal_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "pay_deal"), f"pay_deal_{deal_id}")],
        back_row(lang),
    )


def confirm_kb(deal_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "confirm_receipt"), f"confirm_deal_{deal_id}")],
        back_row(lang),
    )


def balance_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "deposit"), "deposit"), btn(b(lang, "withdraw"), "withdraw")],
        back_row(lang),
    )


def withdraw_currency_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn("⭐ Stars",  "wcur_Stars"), btn("💵 USDT", "wcur_USDT")],
        [btn("💎 TON",   "wcur_TON"),   btn("🇷🇺 RUB",  "wcur_RUB")],
        [btn("🇧🇾 BYN",  "wcur_BYN"),  btn("🇰🇿 KZT",  "wcur_KZT")],
        [btn("🇺🇿 UZS",  "wcur_UZS"),  btn("🇺🇦 UAH",  "wcur_UAH")],
        back_row(lang),
    )


def requisites_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "edit_card"),   "edit_card")],
        [btn(b(lang, "edit_crypto"), "edit_crypto")],
        [btn(b(lang, "edit_wallet"), "edit_wallet")],
        [btn(b(lang, "edit_stars"),  "edit_stars")],
        [btn(b(lang, "create_deal"), "create_deal")],
        back_row(lang),
    )


def referrals_kb(ref_link: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn_url(b(lang, "share_link"), f"https://t.me/share/url?url={ref_link}")],
        back_row(lang),
    )


def withdraw_review_kb(withdraw_id: int) -> InlineKeyboardMarkup:
    # Admin-only keyboard -- stays in Russian, see admin.py.
    return kb([
        btn("✅ Выполнено", f"wd_done_{withdraw_id}"),
        btn("❌ Отклонить", f"wd_reject_{withdraw_id}"),
    ])


def language_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return kb(
        [btn(b(lang, "lang_ru"), "set_lang_ru"), btn(b(lang, "lang_en"), "set_lang_en")],
        back_row(lang),
    )
