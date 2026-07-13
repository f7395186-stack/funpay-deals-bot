from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import database as db
import emojis as em
from helpers import send_msg, bot_send_msg
from config import ADMIN_ID

router = Router()
CUR_SYM = {"Stars": "⭐", "USDT": "💵", "TON": "💎", "RUB": "🇷🇺", "BYN": "🇧🇾", "KZT": "🇰🇿", "UZS": "🇺🇿", "UAH": "🇺🇦"}


def _is_admin(message_or_callback) -> bool:
    return message_or_callback.from_user.id == ADMIN_ID


@router.message(F.text == "/admin", F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    text = (
        f"{em.CROWN} <b>Админ-панель Funpay Deals</b>\n\n"
        f"{em.NOTEPAD} Команды:\n"
        f"<code>/credit user_id CURRENCY сумма</code> — начислить баланс\n"
        f"<code>/debit user_id CURRENCY сумма</code> — списать баланс\n\n"
        f"{em.STAR} Валюты: Stars, USDT, TON, RUB, BYN, KZT, UZS, UAH"
    )
    await send_msg(message, text)


@router.message(F.text.startswith("/credit"), F.from_user.id == ADMIN_ID)
async def admin_credit(message: Message):
    parts = message.text.split()
    if len(parts) != 4:
        await send_msg(message, f"{em.CROSS} Формат: /credit user_id CURRENCY сумма")
        return
    _, uid, currency_raw, amount = parts
    currency = db.normalize_currency(currency_raw)
    try:
        uid = int(uid)
        amount = float(amount.replace(",", "."))
        assert currency and amount > 0
    except Exception:
        await send_msg(message, f"{em.CROSS} Некорректные данные команды.")
        return
    await db.credit_balance(uid, currency, amount)
    sym = CUR_SYM.get(currency, currency)
    await send_msg(message, f"{em.VERIFIED} Начислено {sym} {amount} {currency} пользователю <code>{uid}</code>.")
    try:
        await bot_send_msg(
            message.bot, uid,
            f"{em.MONEYBAG} <b>Баланс пополнен!</b>\n\n{em.DOLLAR} +{sym} {amount} {currency}"
        )
    except Exception:
        pass


@router.message(F.text.startswith("/debit"), F.from_user.id == ADMIN_ID)
async def admin_debit(message: Message):
    parts = message.text.split()
    if len(parts) != 4:
        await send_msg(message, f"{em.CROSS} Формат: /debit user_id CURRENCY сумма")
        return
    _, uid, currency_raw, amount = parts
    currency = db.normalize_currency(currency_raw)
    try:
        uid = int(uid)
        amount = float(amount.replace(",", "."))
        assert currency and amount > 0
    except Exception:
        await send_msg(message, f"{em.CROSS} Некорректные данные команды.")
        return
    ok = await db.debit_balance(uid, currency, amount)
    if not ok:
        await send_msg(message, f"{em.CROSS} У пользователя недостаточно средств.")
        return
    sym = CUR_SYM.get(currency, currency)
    await send_msg(message, f"{em.VERIFIED} Списано {sym} {amount} {currency} у пользователя <code>{uid}</code>.")


@router.callback_query(F.data.startswith("wd_done_"), F.from_user.id == ADMIN_ID)
async def withdraw_mark_done(callback: CallbackQuery):
    withdraw_id = int(callback.data[8:])
    withdrawal = await db.get_withdrawal(withdraw_id)
    if not withdrawal or withdrawal["status"] != "pending":
        await callback.answer("Заявка уже обработана.", show_alert=True)
        return
    await db.update_withdrawal_status(withdraw_id, "done")
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n{em.VERIFIED} <b>Выполнено</b>",
        parse_mode="HTML",
    ) if callback.message.caption else await callback.message.edit_text(
        callback.message.text + f"\n\n{em.VERIFIED} <b>Выполнено</b>", parse_mode="HTML"
    )
    await callback.answer("✅ Отмечено как выполненное.")
    try:
        sym = CUR_SYM.get(withdrawal["currency"], withdrawal["currency"])
        await bot_send_msg(
            callback.bot, withdrawal["user_id"],
            f"{em.VERIFIED} <b>Вывод выполнен!</b>\n\n"
            f"{em.DOLLAR} {sym} {withdrawal['amount']} {withdrawal['currency']} отправлено на <code>{withdrawal['requisite']}</code>."
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("wd_reject_"), F.from_user.id == ADMIN_ID)
async def withdraw_reject(callback: CallbackQuery):
    withdraw_id = int(callback.data[10:])
    withdrawal = await db.get_withdrawal(withdraw_id)
    if not withdrawal or withdrawal["status"] != "pending":
        await callback.answer("Заявка уже обработана.", show_alert=True)
        return
    await db.update_withdrawal_status(withdraw_id, "rejected")
    await db.credit_balance(withdrawal["user_id"], withdrawal["currency"], withdrawal["amount"])
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n{em.CROSS} <b>Отклонено, средства возвращены</b>",
        parse_mode="HTML",
    ) if callback.message.caption else await callback.message.edit_text(
        callback.message.text + f"\n\n{em.CROSS} <b>Отклонено, средства возвращены</b>", parse_mode="HTML"
    )
    await callback.answer("❌ Заявка отклонена, средства возвращены.")
    try:
        sym = CUR_SYM.get(withdrawal["currency"], withdrawal["currency"])
        await bot_send_msg(
            callback.bot, withdrawal["user_id"],
            f"{em.CROSS} <b>Заявка на вывод отклонена</b>\n\n"
            f"{em.WALLET} {sym} {withdrawal['amount']} {withdrawal['currency']} возвращены на баланс."
        )
    except Exception:
        pass
