from aiogram import Router, F
from aiogram.types import CallbackQuery
import database as db
import keyboards as kb
from helpers import edit_msg
from i18n import t

router = Router()


@router.callback_query(F.data == "lang_menu")
async def lang_menu(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    await edit_msg(callback.message, t(lang, "lang_menu_text"), reply_markup=kb.language_kb(lang))
    await callback.answer()


@router.callback_query(F.data.in_({"set_lang_ru", "set_lang_en"}))
async def set_lang(callback: CallbackQuery):
    new_lang = "ru" if callback.data == "set_lang_ru" else "en"
    await db.set_lang(callback.from_user.id, new_lang)
    from handlers.start import welcome_text
    await callback.answer(t(new_lang, f"lang_set_{new_lang}"))
    await edit_msg(callback.message, welcome_text(new_lang), reply_markup=kb.main_menu_kb(new_lang))
