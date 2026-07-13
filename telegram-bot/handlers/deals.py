from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg, bot_send_msg, fmt
from states import DealCreation
from config import SUPPORT_USERNAME, COMMISSION, ADMIN_ID

router = Router()
CUR_SYM = {"Stars": "⭐", "USDT": "💵", "TON": "💎", "RUB": "🇷🇺", "BYN": "🇧🇾", "KZT": "🇰🇿", "UZS": "🇺🇿"}


@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DealCreation.choosing_role)
    text = (
        f"{em.HANDSHAKE} <b>Создание сделки</b>\n\n"
        f"{em.QUESTION} Кем вы выступаете в этой сделке?"
    )
    await edit_msg(callback.message, text, reply_markup=kb.deal_role_kb())
    await callback.answer()


@router.callback_query(DealCreation.choosing_role, F.data.in_({"role_buyer", "role_seller"}))
async def role_chosen(callback: CallbackQuery, state: FSMContext):
    role = "buyer" if callback.data == "role_buyer" else "seller"
    if role == "seller" and not await db.has_requisites(callback.from_user.id):
        await state.clear()
        text = (
            f"{em.IMP1}{em.IMP2}{em.IMP3} <b>Ошибка: не привязаны реквизиты!</b>\n\n"
            f"{em.SHIELD} Мы должны знать, куда переводить деньги.\n"
            f"{em.KEY} Привяжите реквизиты прямо сейчас."
        )
        await edit_msg(callback.message, text, reply_markup=kb.attach_req_kb())
        await callback.answer()
        return
    await state.update_data(role=role)
    await state.set_state(DealCreation.choosing_currency)
    text = (
        f"{em.DOLLAR} <b>Шаг 1 из 3 — Выберите валюту:</b>\n\n"
        f"{em.STAR} Stars · {em.DIAMOND} TON · {em.DOLLAR} USDT · 🇷🇺 RUB · 🇧🇾 BYN · 🇰🇿 KZT · 🇺🇿 UZS"
    )
    await edit_msg(callback.message, text, reply_markup=kb.currency_kb())
    await callback.answer()


@router.callback_query(DealCreation.choosing_currency, F.data.startswith("cur_"))
async def currency_chosen(callback: CallbackQuery, state: FSMContext):
    currency = callback.data[4:]
    await state.update_data(currency=currency)
    await state.set_state(DealCreation.entering_amount)
    text = (
        f"{em.CALC} <b>Шаг 2 из 3 — Введите сумму</b>\n\n"
        f"{em.TIMER} Валюта: {CUR_SYM.get(currency, currency)} <b>{currency}</b>\n\n"
        f"{em.PENCIL} Введите число, например: <code>500</code>"
    )
    await edit_msg(callback.message, text, reply_markup=kb.cancel_kb())
    await callback.answer()


@router.message(DealCreation.entering_amount)
async def amount_entered(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        assert amount > 0
    except Exception:
        await send_msg(message, f"{em.CROSS} <b>Ошибка:</b> Введите число больше нуля.",
                       reply_markup=kb.cancel_kb())
        return
    await state.update_data(amount=amount)
    await state.set_state(DealCreation.entering_description)
    text = (
        f"{em.NOTEPAD} <b>Шаг 3 из 3 — Опишите товар / услугу</b>\n\n"
        f"{em.PENCIL} Пример: <i>Аккаунт Minecraft Premium, 2024</i>"
    )
    await send_msg(message, text, reply_markup=kb.cancel_kb())


@router.message(DealCreation.entering_description)
async def description_entered(message: Message, state: FSMContext):
    desc = message.text.strip()
    if len(desc) < 3:
        await send_msg(message, f"{em.CROSS} Описание слишком короткое. Минимум 3 символа.",
                       reply_markup=kb.cancel_kb())
        return
    data = await state.get_data()
    did  = await db.create_deal(message.from_user.id, data["role"], data["amount"], data["currency"], desc)
    await state.clear()
    me   = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=deal_{did}"
    sym  = CUR_SYM.get(data["currency"], data["currency"])
    text = (
        f"{em.VERIFIED} <b>Сделка создана!</b>\n\n"
        f"{em.GRID} <b>ID:</b> <code>{did}</code>\n"
        f"{em.DOLLAR} <b>Сумма:</b> {sym} {fmt(data['amount'])} {data['currency']}\n"
        f"{em.BRIEFCASE} <b>Описание:</b> {desc}\n"
        f"{em.CLOCK} <b>Статус:</b> Ожидание оплаты\n\n"
        f"{em.LIGHTNING} <b>Ссылка для покупателя:</b>\n<code>{link}</code>\n\n"
        f"{em.SHIELD} Отправьте эту ссылку покупателю."
    )
    await send_msg(message, text, reply_markup=kb.back_kb())

    user = message.from_user
    uname = f"@{user.username}" if user.username else f"id:{user.id}"
    try:
        await bot_send_msg(
            message.bot, ADMIN_ID,
            f"{em.NOTEPAD} <b>Новая сделка создана!</b>\n\n"
            f"ID сделки: <code>{did}</code>\n"
            f"Создал: {uname} (<code>{user.id}</code>)\n"
            f"Роль: {'Продавец' if data['role'] == 'seller' else 'Покупатель'}\n"
            f"Сумма: {sym} {fmt(data['amount'])} {data['currency']}\n"
            f"Товар: {desc}\n\n"
            f"{em.LIGHTNING} <b>Ссылка сделки:</b>\n{link}"
        )
    except Exception:
        pass


async def show_deal_payment(message: Message, deal_id: str):
    deal = await db.get_deal(deal_id)
    if not deal:
        await send_msg(message, f"{em.CROSS} Сделка не найдена.", reply_markup=kb.back_kb())
        return
    if deal["status"] != "pending":
        await send_msg(message, f"{em.CROSS} Сделка недоступна (статус: {deal['status']}).",
                       reply_markup=kb.back_kb())
        return
    sym = CUR_SYM.get(deal["currency"], deal["currency"])
    text = (
        f"{em.SHIELD} <b>Сделка #{deal_id}</b>\n\n"
        f"{em.BRIEFCASE} <b>Описание:</b> {deal['description']}\n"
        f"{em.DOLLAR} <b>Сумма:</b> {sym} {fmt(deal['amount'])} {deal['currency']}\n"
        f"{em.CLOCK} <b>Статус:</b> Ожидание оплаты\n\n"
        f"{em.HANDSHAKE} Нажмите кнопку ниже для оплаты."
    )
    await send_msg(message, text, reply_markup=kb.pay_deal_kb(deal_id))


@router.callback_query(F.data.startswith("pay_deal_"))
async def pay_deal(callback: CallbackQuery):
    deal_id = callback.data[9:]
    deal    = await db.get_deal(deal_id)
    if not deal:
        await callback.answer("❌ Сделка не найдена.", show_alert=True)
        return
    if deal["status"] != "pending":
        await callback.answer("❌ Сделка уже оплачена.", show_alert=True)
        return
    if deal["creator_id"] == callback.from_user.id:
        await callback.answer("❌ Нельзя оплатить свою сделку.", show_alert=True)
        return
    buyer_id = callback.from_user.id
    await db.set_deal_buyer(deal_id, buyer_id)
    await db.update_deal_status(deal_id, "paid")
    sym = CUR_SYM.get(deal["currency"], deal["currency"])
    text = (
        f"{em.VERIFIED} <b>Оплата принята!</b>\n\n"
        f"{em.SHIELD} {sym} {fmt(deal['amount'])} {deal['currency']} заморожено.\n\n"
        f"{em.CLOCK} Ожидайте, пока продавец передаст товар через <b>{SUPPORT_USERNAME}</b>"
    )
    await edit_msg(callback.message, text, reply_markup=kb.confirm_kb(deal_id))
    await callback.answer("✅ Оплата прошла!")

    seller_id = deal["seller_id"] or deal["creator_id"]
    if seller_id and seller_id != buyer_id:
        try:
            await bot_send_msg(
                callback.bot, seller_id,
                f"{em.MONEYBAG} <b>Сделка #{deal_id} оплачена!</b>\n\n"
                f"{em.SHIELD} Деньги ({sym} {fmt(deal['amount'])} {deal['currency']}) заморожены.\n\n"
                f"{em.IMP1}{em.IMP2}{em.IMP3} <b>ВНИМАНИЕ!</b>\n"
                f"Передавайте товар <b>ТОЛЬКО</b> через <b>{SUPPORT_USERNAME}</b>\n\n"
                f"{em.CROSS} Напрямую покупателю — сделка аннулируется!"
            )
        except Exception:
            pass

    buyer = callback.from_user
    uname = f"@{buyer.username}" if buyer.username else f"id:{buyer.id}"
    try:
        me = await callback.bot.get_me()
        link = f"https://t.me/{me.username}?start=deal_{deal_id}"
        await bot_send_msg(
            callback.bot, ADMIN_ID,
            f"{em.CARD} <b>Сделка #{deal_id} оплачена!</b>\n\n"
            f"Покупатель: {uname} (<code>{buyer.id}</code>)\n"
            f"Сумма: {sym} {fmt(deal['amount'])} {deal['currency']}\n"
            f"Товар: {deal['description']}\n\n"
            f"{em.LIGHTNING} <b>Ссылка сделки:</b>\n{link}"
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("confirm_deal_"))
async def confirm_deal(callback: CallbackQuery):
    deal_id = callback.data[13:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer("❌ Сделка не найдена.", show_alert=True)
        return
    if deal["status"] != "paid":
        await callback.answer("❌ Сделку нельзя подтвердить на этом этапе.", show_alert=True)
        return
    if deal["buyer_id"] != callback.from_user.id:
        await callback.answer("❌ Подтвердить может только покупатель.", show_alert=True)
        return

    seller_id = deal["seller_id"] or deal["creator_id"]
    commission = deal["amount"] * COMMISSION
    payout = deal["amount"] - commission
    await db.credit_balance(seller_id, deal["currency"], payout)
    await db.update_deal_status(deal_id, "completed")

    sym = CUR_SYM.get(deal["currency"], deal["currency"])
    text = (
        f"{em.VERIFIED} <b>Сделка #{deal_id} завершена!</b>\n\n"
        f"{em.SHIELD} Спасибо, что пользуетесь Funpay Deals.\n"
        f"{em.CHART} Продавцу зачислено {sym} {fmt(payout)} {deal['currency']} (комиссия {int(COMMISSION*100)}%)."
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb())
    await callback.answer("✅ Сделка завершена!")

    if seller_id != callback.from_user.id:
        try:
            await bot_send_msg(
                callback.bot, seller_id,
                f"{em.MONEYBAG} <b>Сделка #{deal_id} завершена!</b>\n\n"
                f"{em.CHECK} Покупатель подтвердил получение товара.\n"
                f"{em.DOLLAR} На баланс зачислено: {sym} {fmt(payout)} {deal['currency']}\n\n"
                f"{em.WALLET} Вывести средства можно в разделе «Баланс»."
            )
        except Exception:
            pass

    try:
        await bot_send_msg(
            callback.bot, ADMIN_ID,
            f"{em.VERIFIED} <b>Сделка #{deal_id} завершена!</b>\n\n"
            f"Продавцу ({seller_id}) начислено {sym} {fmt(payout)} {deal['currency']}\n"
            f"Комиссия сервиса: {sym} {fmt(commission)} {deal['currency']}"
        )
    except Exception:
        pass
