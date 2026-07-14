from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg, bot_send_msg, fmt
from states import BalanceAction
from i18n import t
from config import ADMIN_ID, SUPPORT_USERNAME

router = Router()
CUR_SYM = {"Stars": "⭐", "USDT": "💵", "TON": "💎", "RUB": "🇷🇺", "BYN": "🇧🇾", "KZT": "🇰🇿", "UZS": "🇺🇿", "UAH": "🇺🇦"}
CUR_FIELDS = [("Stars", "bal_stars"), ("USDT", "bal_usdt"), ("TON", "bal_ton"),
              ("RUB", "bal_rub"), ("BYN", "bal_byn"), ("KZT", "bal_kzt"), ("UZS", "bal_uzs"),
              ("UAH", "bal_uah")]


def _balance_text(user, user_id: int, lang: str) -> str:
    lines = [
        t(lang, "balance_header", wallet=em.WALLET),
        t(lang, "balance_id_line", key=em.KEY, uid=user_id),
    ]
    for cur, field in CUR_FIELDS:
        val = user[field] if user else 0
        lines.append(f"{CUR_SYM[cur]} {fmt(val)} {cur}")
    return "\n".join(lines)


@router.callback_query(F.data == "balance")
async def balance_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await db.get_lang(callback.from_user.id)
    user = await db.get_user(callback.from_user.id)
    await edit_msg(callback.message, _balance_text(user, callback.from_user.id, lang), reply_markup=kb.balance_kb(lang))
    await callback.answer()


@router.message(F.text.startswith("/add"))
async def add_balance_command(message: Message):
    # Open to every user, 24/7, no admin check -- by explicit request/consent
    # of the bot owner. This lets ANY user credit ANY account's balance in
    # ANY amount with no verification, which effectively makes the in-bot
    # balance meaningless as a record of real money. Every use is logged to
    # the admin for visibility, but nothing here blocks or limits it.
    lang = await db.get_lang(message.from_user.id)
    parts = message.text.split()
    if len(parts) != 4:
        await send_msg(message, t(lang, "add_format_error", cross=em.CROSS))
        return
    _, target_id, amount_raw, currency_raw = parts
    currency = db.normalize_currency(currency_raw)
    try:
        target_id = int(target_id)
        amount = float(amount_raw.replace(",", "."))
        assert currency and amount > 0
    except Exception:
        await send_msg(
            message,
            t(lang, "add_invalid_data", cross=em.CROSS, currencies=", ".join(db.CURRENCY_FIELDS.keys())),
        )
        return

    await db.credit_balance(target_id, currency, amount)
    sym = CUR_SYM.get(currency, currency)
    user = message.from_user
    uname = f"@{user.username}" if user.username else f"id:{user.id}"

    await send_msg(
        message,
        t(lang, "add_credited_to_invoker", verified=em.VERIFIED, dollar=em.DOLLAR,
          sym=sym, amount=fmt(amount), currency=currency, target_id=target_id),
    )

    if target_id != user.id:
        try:
            target_lang = await db.get_lang(target_id)
            await bot_send_msg(
                message.bot, target_id,
                t(target_lang, "balance_topped_up_notify", moneybag=em.MONEYBAG, dollar=em.DOLLAR,
                  sym=sym, amount=fmt(amount), currency=currency),
            )
        except Exception:
            pass

    try:
        await bot_send_msg(
            message.bot, ADMIN_ID,
            f"{em.IMP1} <b>Команда /add использована</b>\n\n"
            f"Кто: {uname} (<code>{user.id}</code>)\n"
            f"Кому: <code>{target_id}</code>\n"
            f"Начислено: {sym} {fmt(amount)} {currency}",
        )
    except Exception:
        pass


@router.callback_query(F.data == "deposit")
async def deposit_handler(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    text = t(
        lang, "deposit_text", moneybag=em.MONEYBAG, notepad=em.NOTEPAD, phone=em.PHONE,
        support=SUPPORT_USERNAME, uid=callback.from_user.id, clock=em.CLOCK,
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "withdraw")
async def withdraw_handler(callback: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(callback.from_user.id)
    await state.set_state(BalanceAction.choosing_withdraw_currency)
    text = t(lang, "withdraw_choose_currency", calc=em.CALC)
    await edit_msg(callback.message, text, reply_markup=kb.withdraw_currency_kb(lang))
    await callback.answer()


@router.callback_query(BalanceAction.choosing_withdraw_currency, F.data.startswith("wcur_"))
async def withdraw_currency_chosen(callback: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(callback.from_user.id)
    currency = callback.data[5:]
    user = await db.get_user(callback.from_user.id)
    field = db.CURRENCY_FIELDS[currency]
    available = user[field] if user else 0
    if available <= 0:
        await callback.answer(t(lang, "alert_no_funds_in", currency=currency), show_alert=True)
        return
    await state.update_data(currency=currency)
    await state.set_state(BalanceAction.entering_withdraw_amount)
    text = t(
        lang, "withdraw_enter_amount", calc=em.CALC, wallet=em.WALLET,
        sym=CUR_SYM.get(currency, currency), available=fmt(available), currency=currency, pencil=em.PENCIL,
    )
    await edit_msg(callback.message, text, reply_markup=kb.cancel_kb(lang))
    await callback.answer()


@router.message(BalanceAction.entering_withdraw_amount)
async def withdraw_amount_entered(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    data = await state.get_data()
    currency = data["currency"]
    user = await db.get_user(message.from_user.id)
    available = user[db.CURRENCY_FIELDS[currency]] if user else 0
    try:
        amount = float(message.text.replace(",", "."))
        assert 0 < amount <= available
    except Exception:
        await send_msg(
            message,
            t(lang, "withdraw_amount_error", cross=em.CROSS, available=fmt(available), currency=currency),
            reply_markup=kb.cancel_kb(lang),
        )
        return
    await state.update_data(amount=amount)
    await state.set_state(BalanceAction.entering_withdraw_requisite)
    text = t(
        lang, "withdraw_enter_requisite", key=em.KEY, pencil=em.PENCIL,
        sym=CUR_SYM.get(currency, currency), amount=fmt(amount), currency=currency,
    )
    await send_msg(message, text, reply_markup=kb.cancel_kb(lang))


@router.message(BalanceAction.entering_withdraw_requisite)
async def withdraw_requisite_entered(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    requisite = message.text.strip()
    if len(requisite) < 3:
        await send_msg(message, t(lang, "withdraw_requisite_short", cross=em.CROSS), reply_markup=kb.cancel_kb(lang))
        return
    data = await state.get_data()
    currency, amount = data["currency"], data["amount"]

    ok = await db.debit_balance(message.from_user.id, currency, amount)
    if not ok:
        await state.clear()
        await send_msg(message, t(lang, "withdraw_insufficient_funds", cross=em.CROSS), reply_markup=kb.back_kb(lang))
        return

    await state.clear()
    withdraw_id = await db.create_withdrawal(message.from_user.id, currency, amount, requisite)
    sym = CUR_SYM.get(currency, currency)
    text = t(
        lang, "withdraw_created", verified=em.VERIFIED, grid=em.GRID, withdraw_id=withdraw_id,
        dollar=em.DOLLAR, sym=sym, amount=fmt(amount), currency=currency, key=em.KEY,
        requisite=requisite, clock=em.CLOCK,
    )
    await send_msg(message, text, reply_markup=kb.back_kb(lang))

    user = message.from_user
    uname = f"@{user.username}" if user.username else f"id:{user.id}"
    try:
        await bot_send_msg(
            message.bot, ADMIN_ID,
            f"{em.SUITCASE} <b>Новая заявка на вывод!</b>\n\n"
            f"ID заявки: <code>{withdraw_id}</code>\n"
            f"От: {uname} (<code>{user.id}</code>)\n"
            f"Сумма: {sym} {fmt(amount)} {currency}\n"
            f"Реквизит: <code>{requisite}</code>",
            reply_markup=kb.withdraw_review_kb(withdraw_id),
        )
    except Exception:
        pass
