from aiogram import Router, F
from aiogram.types import CallbackQuery
import database as db
import keyboards as kb
import emojis as em
from helpers import edit_msg

router = Router()


@router.callback_query(F.data == "referrals")
async def referrals_handler(callback: CallbackQuery):
    me = await callback.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref{callback.from_user.id}"
    count = await db.count_referrals(callback.from_user.id)
    text = (
        f"{em.GIFT} <b>Реферальная программа</b>\n\n"
        f"{em.PEOPLE} Приглашено друзей: <b>{count}</b>\n\n"
        f"{em.LIGHTNING} Ваша реферальная ссылка:\n<code>{link}</code>\n\n"
        f"{em.STAR} Делитесь ссылкой — приглашённые друзья закрепляются за вами навсегда."
    )
    await edit_msg(callback.message, text, reply_markup=kb.referrals_kb(link))
    await callback.answer()
