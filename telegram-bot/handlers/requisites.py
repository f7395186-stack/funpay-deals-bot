from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import emojis as em
from helpers import send_msg, edit_msg
from states import RequisiteEdit

router = Router()

FIELD_MAP = {
    "edit_card":   ("card", RequisiteEdit.editing_card, f"{em.CARD} Введите номер карты:"),
    "edit_crypto": ("crypto", RequisiteEdit.editing_crypto, f"{em.BITCOIN} Введите адрес криптокошелька:"),
    "edit_wallet": ("wallet", RequisiteEdit.editing_wallet, f"{em.WALLET} Введите номер/адрес электронного кошелька:"),
    "edit_stars":  ("stars_username", RequisiteEdit.editing_stars, f"{em.STAR} Введите ваш username для получения Stars (например @username):"),
}


def _mask(value: str) -> str:
    value = (value or "").strip()
    return value if value else "не указано"


def _requisites_text(user) -> str:
    return (
        f"{em.KEY} <b>Ваши реквизиты</b>\n\n"
        f"{em.CARD} Карта: <code>{_mask(user['card'] if user else '')}</code>\n"
        f"{em.BITCOIN} Крипта: <code>{_mask(user['crypto'] if user else '')}</code>\n"
        f"{em.WALLET} Кошелёк: <code>{_mask(user['wallet'] if user else '')}</code>\n"
        f"{em.STAR} Stars username: <code>{_mask(user['stars_username'] if user else '')}</code>\n\n"
        f"{em.PENCIL} Выберите, что изменить:"
    )


@router.callback_query(F.data == "requisites")
async def requisites_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(callback.from_user.id)
    await edit_msg(callback.message, _requisites_text(user), reply_markup=kb.requisites_kb())
    await callback.answer()


@router.callback_query(F.data.in_(FIELD_MAP.keys()))
async def edit_requisite_start(callback: CallbackQuery, state: FSMContext):
    field, target_state, prompt = FIELD_MAP[callback.data]
    await state.set_state(target_state)
    await edit_msg(callback.message, prompt, reply_markup=kb.cancel_kb())
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
    value = message.text.strip()
    if len(value) < 3:
        await send_msg(message, f"{em.CROSS} Значение слишком короткое, минимум 3 символа.", reply_markup=kb.cancel_kb())
        return
    await db.update_requisite(message.from_user.id, field, value)
    await state.clear()
    await send_msg(
        message,
        f"{em.VERIFIED} <b>Реквизит сохранён!</b>\n\n{em.CHECK} <code>{value}</code>",
        reply_markup=kb.requisites_kb(),
    )
