from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg, bot_send_msg, fmt
from states import DealCreation
from i18n import t
from config import SUPPORT_USERNAME, COMMISSION, ADMIN_ID

router = Router()
CUR_SYM = {"Stars": "⭐", "USDT": "💵", "TON": "💎", "RUB": "🇷🇺", "BYN": "🇧🇾", "KZT": "🇰🇿", "UZS": "🇺🇿", "UAH": "🇺🇦"}


@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DealCreation.choosing_role)
    lang = await db.get_lang(callback.from_user.id)
    text = t(lang, "deal_role_prompt", handshake=em.HANDSHAKE, question=em.QUESTION)
    await edit_msg(callback.message, text, reply_markup=kb.deal_role_kb(lang))
    await callback.answer()


@router.callback_query(DealCreation.choosing_role, F.data.in_({"role_buyer", "role_seller"}))
async def role_chosen(callback: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(callback.from_user.id)
    role = "buyer" if callback.data == "role_buyer" else "seller"
    if role == "seller" and not await db.has_requisites(callback.from_user.id):
        await state.clear()
        text = t(
            lang, "deal_no_requisites",
            imp1=em.IMP1, imp2=em.IMP2, imp3=em.IMP3, shield=em.SHIELD, key=em.KEY,
        )
        await edit_msg(callback.message, text, reply_markup=kb.attach_req_kb(lang))
        await callback.answer()
        return
    await state.update_data(role=role)
    await state.set_state(DealCreation.choosing_currency)
    text = t(lang, "deal_choose_currency", dollar=em.DOLLAR, star=em.STAR, diamond=em.DIAMOND)
    await edit_msg(callback.message, text, reply_markup=kb.currency_kb(lang))
    await callback.answer()


@router.callback_query(DealCreation.choosing_currency, F.data.startswith("cur_"))
async def currency_chosen(callback: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(callback.from_user.id)
    currency = callback.data[4:]
    await state.update_data(currency=currency)
    await state.set_state(DealCreation.entering_amount)
    text = t(
        lang, "deal_enter_amount", calc=em.CALC, timer=em.TIMER,
        sym=CUR_SYM.get(currency, currency), currency=currency, pencil=em.PENCIL,
    )
    await edit_msg(callback.message, text, reply_markup=kb.cancel_kb(lang))
    await callback.answer()


@router.message(DealCreation.entering_amount)
async def amount_entered(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    try:
        amount = float(message.text.replace(",", "."))
        assert amount > 0
    except Exception:
        await send_msg(message, t(lang, "deal_amount_error", cross=em.CROSS), reply_markup=kb.cancel_kb(lang))
        return
    await state.update_data(amount=amount)
    await state.set_state(DealCreation.entering_description)
    text = t(lang, "deal_enter_description", notepad=em.NOTEPAD, pencil=em.PENCIL)
    await send_msg(message, text, reply_markup=kb.cancel_kb(lang))


@router.message(DealCreation.entering_description)
async def description_entered(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    desc = message.text.strip()
    if len(desc) < 3:
        await send_msg(message, t(lang, "deal_desc_too_short", cross=em.CROSS), reply_markup=kb.cancel_kb(lang))
        return
    data = await state.get_data()
    did  = await db.create_deal(message.from_user.id, data["role"], data["amount"], data["currency"], desc)
    await state.clear()
    me   = await message.bot.get_me()
    link = f"https://t.me/{me.username}?start=deal_{did}"
    sym  = CUR_SYM.get(data["currency"], data["currency"])
    text = t(
        lang, "deal_created",
        verified=em.VERIFIED, grid=em.GRID, did=did, dollar=em.DOLLAR,
        sym=sym, amount=fmt(data["amount"]), currency=data["currency"],
        briefcase=em.BRIEFCASE, desc=desc, clock=em.CLOCK,
        lightning=em.LIGHTNING, link=link, shield=em.SHIELD,
    )
    await send_msg(message, text, reply_markup=kb.back_kb(lang))

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


async def show_deal_payment(message: Message, deal_id: str, lang: str | None = None):
    if lang is None:
        lang = await db.get_lang(message.from_user.id)
    deal = await db.get_deal(deal_id)
    if not deal:
        await send_msg(message, t(lang, "deal_not_found", cross=em.CROSS), reply_markup=kb.back_kb(lang))
        return
    if deal["status"] != "pending":
        await send_msg(
            message, t(lang, "deal_unavailable", cross=em.CROSS, status=deal["status"]),
            reply_markup=kb.back_kb(lang),
        )
        return
    sym = CUR_SYM.get(deal["currency"], deal["currency"])
    text = t(
        lang, "deal_payment_prompt",
        shield=em.SHIELD, deal_id=deal_id, briefcase=em.BRIEFCASE, desc=deal["description"],
        dollar=em.DOLLAR, sym=sym, amount=fmt(deal["amount"]), currency=deal["currency"],
        clock=em.CLOCK, handshake=em.HANDSHAKE,
    )
    await send_msg(message, text, reply_markup=kb.pay_deal_kb(deal_id, lang))


@router.callback_query(F.data.startswith("pay_deal_"))
async def pay_deal(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    deal_id = callback.data[9:]
    deal    = await db.get_deal(deal_id)
    if not deal:
        await callback.answer(t(lang, "alert_deal_not_found"), show_alert=True)
        return
    if deal["status"] != "pending":
        await callback.answer(t(lang, "alert_deal_already_paid"), show_alert=True)
        return
    if deal["creator_id"] == callback.from_user.id:
        await callback.answer(t(lang, "alert_cant_pay_own"), show_alert=True)
        return
    buyer_id = callback.from_user.id
    await db.set_deal_buyer(deal_id, buyer_id)
    await db.update_deal_status(deal_id, "paid")
    sym = CUR_SYM.get(deal["currency"], deal["currency"])
    text = t(
        lang, "deal_payment_accepted",
        verified=em.VERIFIED, shield=em.SHIELD, sym=sym, amount=fmt(deal["amount"]),
        currency=deal["currency"], clock=em.CLOCK, support=SUPPORT_USERNAME,
    )
    await edit_msg(callback.message, text, reply_markup=kb.confirm_kb(deal_id, lang))
    await callback.answer(t(lang, "alert_payment_success"))

    seller_id = deal["seller_id"] or deal["creator_id"]
    if seller_id and seller_id != buyer_id:
        try:
            seller_lang = await db.get_lang(seller_id)
            await bot_send_msg(
                callback.bot, seller_id,
                t(
                    seller_lang, "deal_paid_notify_seller",
                    moneybag=em.MONEYBAG, deal_id=deal_id, shield=em.SHIELD, sym=sym,
                    amount=fmt(deal["amount"]), currency=deal["currency"],
                    imp1=em.IMP1, imp2=em.IMP2, imp3=em.IMP3, support=SUPPORT_USERNAME, cross=em.CROSS,
                ),
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
    lang = await db.get_lang(callback.from_user.id)
    deal_id = callback.data[13:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer(t(lang, "alert_deal_not_found"), show_alert=True)
        return
    if deal["status"] != "paid":
        await callback.answer(t(lang, "alert_cant_confirm_stage"), show_alert=True)
        return
    if deal["buyer_id"] != callback.from_user.id:
        await callback.answer(t(lang, "alert_only_buyer_confirm"), show_alert=True)
        return

    seller_id = deal["seller_id"] or deal["creator_id"]
    commission = deal["amount"] * COMMISSION
    payout = deal["amount"] - commission
    await db.credit_balance(seller_id, deal["currency"], payout)
    await db.update_deal_status(deal_id, "completed")

    sym = CUR_SYM.get(deal["currency"], deal["currency"])
    text = t(
        lang, "deal_completed_buyer",
        verified=em.VERIFIED, deal_id=deal_id, shield=em.SHIELD, chart=em.CHART,
        sym=sym, payout=fmt(payout), currency=deal["currency"], commission_pct=int(COMMISSION * 100),
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb(lang))
    await callback.answer(t(lang, "alert_deal_completed"))

    if seller_id != callback.from_user.id:
        try:
            seller_lang = await db.get_lang(seller_id)
            await bot_send_msg(
                callback.bot, seller_id,
                t(
                    seller_lang, "deal_completed_notify_seller",
                    moneybag=em.MONEYBAG, deal_id=deal_id, check=em.CHECK, dollar=em.DOLLAR,
                    sym=sym, payout=fmt(payout), currency=deal["currency"], wallet=em.WALLET,
                ),
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
