from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg, bot_send_msg, fmt
from states import BalanceAction
from config import ADMIN_ID, SUPPORT_USERNAME

router = Router()
CUR_SYM = {"Stars": "⭐", "USDT": "💵", "TON": "💎", "RUB": "🇷🇺", "BYN": "🇧🇾", "KZT": "🇰🇿", "UZS": "🇺🇿"}
CUR_FIELDS = [("Stars", "bal_stars"), ("USDT", "bal_usdt"), ("TON", "bal_ton"),
              ("RUB", "bal_rub"), ("BYN", "bal_byn"), ("KZT", "bal_kzt"), ("UZS", "bal_uzs")]


def _balance_text(user) -> str:
    lines = [f"{em.WALLET} <b>Ваш баланс</b>\n"]
    for cur, field in CUR_FIELDS:
        val = user[field] if user else 0
        lines.append(f"{CUR_SYM[cur]} {fmt(val)} {cur}")
    return "\n".join(lines)


@router.callback_query(F.data == "balance")
async def balance_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(callback.from_user.id)
    await edit_msg(callback.message, _balance_text(user), reply_markup=kb.balance_kb())
    await callback.answer()


@router.callback_query(F.data == "deposit")
async def deposit_handler(callback: CallbackQuery):
    text = (
        f"{em.MONEYBAG} <b>Пополнение баланса</b>\n\n"
        f"{em.NOTEPAD} Пополнение проходит через оператора, чтобы гарантировать безопасность средств.\n\n"
        f"{em.PHONE} Напишите в поддержку <b>{SUPPORT_USERNAME}</b> и укажите:\n"
        f"— сумму и валюту пополнения\n"
        f"— ваш ID: <code>{callback.from_user.id}</code>\n\n"
        f"{em.CLOCK} Баланс будет зачислен после подтверждения оплаты."
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb())
    await callback.answer()


@router.callback_query(F.data == "withdraw")
async def withdraw_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BalanceAction.choosing_withdraw_currency)
    text = f"{em.CALC} <b>Вывод средств — выберите валюту:</b>"
    await edit_msg(callback.message, text, reply_markup=kb.withdraw_currency_kb())
    await callback.answer()


@router.callback_query(BalanceAction.choosing_withdraw_currency, F.data.startswith("wcur_"))
async def withdraw_currency_chosen(callback: CallbackQuery, state: FSMContext):
    currency = callback.data[5:]
    user = await db.get_user(callback.from_user.id)
    field = db.CURRENCY_FIELDS[currency]
    available = user[field] if user else 0
    if available <= 0:
        await callback.answer(f"❌ У вас нет средств в {currency}.", show_alert=True)
        return
    await state.update_data(currency=currency)
    await state.set_state(BalanceAction.entering_withdraw_amount)
    text = (
        f"{em.CALC} <b>Введите сумму вывода</b>\n\n"
        f"{em.WALLET} Доступно: {CUR_SYM.get(currency, currency)} {fmt(available)} {currency}\n\n"
        f"{em.PENCIL} Введите число, например: <code>100</code>"
    )
    await edit_msg(callback.message, text, reply_markup=kb.cancel_kb())
    await callback.answer()


@router.message(BalanceAction.entering_withdraw_amount)
async def withdraw_amount_entered(message: Message, state: FSMContext):
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
            f"{em.CROSS} <b>Ошибка:</b> введите число от 0 до {fmt(available)} {currency}.",
            reply_markup=kb.cancel_kb(),
        )
        return
    await state.update_data(amount=amount)
    await state.set_state(BalanceAction.entering_withdraw_requisite)
    text = (
        f"{em.KEY} <b>Укажите реквизит для вывода</b>\n\n"
        f"{em.PENCIL} Введите карту, кошелёк или username, куда вывести {CUR_SYM.get(currency, currency)} {fmt(amount)} {currency}."
    )
    await send_msg(message, text, reply_markup=kb.cancel_kb())


@router.message(BalanceAction.entering_withdraw_requisite)
async def withdraw_requisite_entered(message: Message, state: FSMContext):
    requisite = message.text.strip()
    if len(requisite) < 3:
        await send_msg(message, f"{em.CROSS} Реквизит слишком короткий.", reply_markup=kb.cancel_kb())
        return
    data = await state.get_data()
    currency, amount = data["currency"], data["amount"]

    ok = await db.debit_balance(message.from_user.id, currency, amount)
    if not ok:
        await state.clear()
        await send_msg(message, f"{em.CROSS} Недостаточно средств.", reply_markup=kb.back_kb())
        return

    await state.clear()
    withdraw_id = await db.create_withdrawal(message.from_user.id, currency, amount, requisite)
    sym = CUR_SYM.get(currency, currency)
    text = (
        f"{em.VERIFIED} <b>Заявка на вывод создана!</b>\n\n"
        f"{em.GRID} <b>ID заявки:</b> <code>{withdraw_id}</code>\n"
        f"{em.DOLLAR} <b>Сумма:</b> {sym} {fmt(amount)} {currency}\n"
        f"{em.KEY} <b>Реквизит:</b> <code>{requisite}</code>\n\n"
        f"{em.CLOCK} Выплата обрабатывается вручную, обычно в течение 24 часов."
    )
    await send_msg(message, text, reply_markup=kb.back_kb())

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
