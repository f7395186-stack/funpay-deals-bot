from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg, bot_send_msg
from config import ADMIN_ID

router = Router()

WELCOME = (
    f"{em.STAR} <b>Добро пожаловать в Funpay Deals Bot</b> — "
    f"ваш надёжный сервис безопасных сделок! {em.SHIELD}\n\n"
    f"{em.LIGHTNING} Автоматизированные сделки\n"
    f"{em.DIAMOND} Поддержка 7 валют\n"
    f"{em.CHART} Реферальная система\n"
    f"{em.WALLET} Вывод в любой валюте\n"
    f"{em.CLOCK24} Поддержка 24/7\n\n"
    f"{em.HANDSHAKE} <b>Выберите раздел ниже!</b>"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    args = message.text.split(maxsplit=1)
    param = args[1] if len(args) > 1 else ""
    referrer_id = deal_id = None

    if param.startswith("ref"):
        try:
            referrer_id = int(param[3:])
            if referrer_id == user.id:
                referrer_id = None
        except ValueError:
            pass
    elif param.startswith("deal_"):
        deal_id = param[5:]

    is_new = await db.register_user(user.id, user.username, referrer_id)
    if not is_new:
        await db.update_username(user.id, user.username)

    if is_new:
        uname = f"@{user.username}" if user.username else f"id:{user.id}"
        try:
            await bot_send_msg(
                message.bot, ADMIN_ID,
                f"{em.PEOPLE} <b>Новый пользователь!</b>\n\n"
                f"Имя: {user.full_name}\n"
                f"Username: {uname}\n"
                f"ID: <code>{user.id}</code>"
            )
        except Exception:
            pass

    if deal_id:
        deal = await db.get_deal(deal_id)
        if deal and deal["status"] == "pending" and deal["creator_id"] != user.id:
            from handlers.deals import show_deal_payment
            await show_deal_payment(message, deal_id)
            return

    await send_msg(message, WELCOME, reply_markup=kb.main_menu_kb())


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await edit_msg(callback.message, WELCOME, reply_markup=kb.main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "faq")
async def faq_handler(callback: CallbackQuery):
    text = (
        f"{em.SHIELD} <b>F.A.Q — Часто задаваемые вопросы</b>\n\n"
        f"{em.CHECK} <b>Как работает гарант?</b>\n"
        "Покупатель платит — деньги замораживаются. "
        "Продавец передаёт товар через @Funpay_Support_Deals. "
        "После подтверждения — деньги у продавца.\n\n"
        f"{em.DOLLAR} <b>Комиссия:</b> 5%\n\n"
        f"{em.STAR} <b>Валюты:</b> Stars · USDT · TON · RUB · BYN · KZT · UZS\n\n"
        f"{em.WALLET} <b>Вывод:</b> «Баланс» → «Вывести»\n\n"
        f"{em.PHONE} Поддержка: <b>@Funpay_Support_Deals</b>"
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb())
    await callback.answer()


@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    text = (
        f"{em.GEAR} <b>Поддержка Funpay Deals</b>\n\n"
        f"{em.PHONE} Аккаунт: <b>@Funpay_Support_Deals</b>\n\n"
        f"{em.CLOCK} Время ответа: до 15 минут\n"
        f"{em.SHIELD} Работаем 24/7 без выходных."
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb())
    await callback.answer()
