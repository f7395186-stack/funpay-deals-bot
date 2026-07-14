from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg, bot_send_msg
from i18n import t
from config import ADMIN_ID, SUPPORT_USERNAME

router = Router()


def welcome_text(lang: str) -> str:
    return t(
        lang, "welcome",
        star=em.STAR, shield=em.SHIELD, lightning=em.LIGHTNING, diamond=em.DIAMOND,
        chart=em.CHART, wallet=em.WALLET, clock24=em.CLOCK24, handshake=em.HANDSHAKE,
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

    lang = await db.get_lang(user.id)

    if deal_id:
        deal = await db.get_deal(deal_id)
        if deal and deal["status"] == "pending" and deal["creator_id"] != user.id:
            from handlers.deals import show_deal_payment
            await show_deal_payment(message, deal_id, lang)
            return

    await send_msg(message, welcome_text(lang), reply_markup=kb.main_menu_kb(lang))


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await db.get_lang(callback.from_user.id)
    await edit_msg(callback.message, welcome_text(lang), reply_markup=kb.main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "faq")
async def faq_handler(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    text = t(
        lang, "faq",
        shield=em.SHIELD, check=em.CHECK, dollar=em.DOLLAR, star=em.STAR,
        wallet=em.WALLET, phone=em.PHONE, support=SUPPORT_USERNAME,
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    text = t(
        lang, "support",
        gear=em.GEAR, phone=em.PHONE, support=SUPPORT_USERNAME, clock=em.CLOCK, shield=em.SHIELD,
    )
    await edit_msg(callback.message, text, reply_markup=kb.back_kb(lang))
    await callback.answer()
