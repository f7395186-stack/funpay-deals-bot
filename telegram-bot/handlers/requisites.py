from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg
from states import RequisiteEdit
from i18n import t

router = Router()

FIELD_MAP = {
    "edit_card":   ("card", RequisiteEdit.editing_card, "prompt_edit_card", {"card": em.CARD}),
    "edit_crypto": ("crypto", RequisiteEdit.editing_crypto, "prompt_edit_crypto", {"bitcoin": em.BITCOIN}),
    "edit_wallet": ("wallet", RequisiteEdit.editing_wallet, "prompt_edit_wallet", {"wallet": em.WALLET}),
    "edit_stars":  ("stars_username", RequisiteEdit.editing_stars, "prompt_edit_stars", {"star": em.STAR}),
}


def _mask(value: str, lang: str) -> str:
    value = (value or "").strip()
    return value if value else t(lang, "not_set")


def _requisites_text(user, lang: str) -> str:
    return t(
        lang, "requisites_text",
        key=em.KEY, card=em.CARD, card_val=_mask(user["card"] if user else "", lang),
        bitcoin=em.BITCOIN, crypto_val=_mask(user["crypto"] if user else "", lang),
        wallet=em.WALLET, wallet_val=_mask(user["wallet"] if user else "", lang),
        star=em.STAR, stars_val=_mask(user["stars_username"] if user else "", lang),
        pencil=em.PENCIL,
    )


@router.callback_query(F.data == "requisites")
async def requisites_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await db.get_lang(callback.from_user.id)
    user = await db.get_user(callback.from_user.id)
    await edit_msg(callback.message, _requisites_text(user, lang), reply_markup=kb.requisites_kb(lang))
    await callback.answer()


@router.callback_query(F.data.in_(FIELD_MAP.keys()))
async def edit_requisite_start(callback: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(callback.from_user.id)
    field, target_state, prompt_key, prompt_kwargs = FIELD_MAP[callback.data]
    await state.set_state(target_state)
    prompt = t(lang, prompt_key, **prompt_kwargs)
    await edit_msg(callback.message, prompt, reply_markup=kb.cancel_kb(lang))
    await callback.answer()


@router.message(RequisiteEdit.editing_card)
async def save_card(message: Message, state: FSMContext):
    await _save_field(message, state, "card")


@router.message(RequisiteEdit.editing_crypto)
async def save_crypto(message: Message, state: FSMContext):
    await _save_field(message, state, "crypto")


@router.message(RequisiteEdit.editing_wallet)
async def save_wallet(message: Message, state: FSMContext):
    await _save_field(message, state, "wallet")


@router.message(RequisiteEdit.editing_stars)
async def save_stars(message: Message, state: FSMContext):
    await _save_field(message, state, "stars_username")


async def _save_field(message: Message, state: FSMContext, field: str):
    lang = await db.get_lang(message.from_user.id)
    value = message.text.strip()
    if len(value) < 3:
        await send_msg(message, t(lang, "requisite_too_short", cross=em.CROSS), reply_markup=kb.cancel_kb(lang))
        return
    await db.update_requisite(message.from_user.id, field, value)
    await state.clear()
    await send_msg(
        message,
        t(lang, "requisite_saved", verified=em.VERIFIED, check=em.CHECK, value=value),
        reply_markup=kb.requisites_kb(lang),
    )
