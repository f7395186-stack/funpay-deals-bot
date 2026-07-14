from aiogram import Router, F
from aiogram.types import CallbackQuery
import database as db
import keyboards as kb
import emojis as em
from helpers import edit_msg
from i18n import t

router = Router()


@router.callback_query(F.data == "referrals")
async def referrals_handler(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    me = await callback.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref{callback.from_user.id}"
    count = await db.count_referrals(callback.from_user.id)
    text = t(
        lang, "referrals_text", gift=em.GIFT, people=em.PEOPLE, count=count,
        lightning=em.LIGHTNING, link=link, star=em.STAR,
    )
    await edit_msg(callback.message, text, reply_markup=kb.referrals_kb(link, lang))
    await callback.answer()
