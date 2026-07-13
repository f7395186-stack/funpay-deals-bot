import os
from aiogram import Bot
from aiogram.types import Message, FSInputFile, InputMediaPhoto

PHOTO_PATH = os.path.join(os.path.dirname(__file__), "funpay_banner.jpg")
_PHOTO_FILE_ID: str | None = None


def _get_photo():
    global _PHOTO_FILE_ID
    if _PHOTO_FILE_ID:
        return _PHOTO_FILE_ID
    return FSInputFile(PHOTO_PATH)


def _has_photo() -> bool:
    return bool(_PHOTO_FILE_ID) or os.path.exists(PHOTO_PATH)


def _cache(msg: Message):
    global _PHOTO_FILE_ID
    if not _PHOTO_FILE_ID and msg and msg.photo:
        _PHOTO_FILE_ID = msg.photo[-1].file_id


async def send_msg(target: Message, text: str, reply_markup=None) -> Message:
    if not _has_photo():
        return await target.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    sent = await target.answer_photo(
        photo=_get_photo(),
        caption=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )
    _cache(sent)
    return sent


async def edit_msg(message: Message, text: str, reply_markup=None):
    try:
        if message.photo or message.document or message.video or message.animation:
            await message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        elif _has_photo():
            await message.edit_media(
                InputMediaPhoto(media=_get_photo(), caption=text, parse_mode="HTML"),
                reply_markup=reply_markup,
            )
        else:
            await message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        try:
            await message.delete()
        except Exception:
            pass
        if not _has_photo():
            sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            sent = await message.answer_photo(
                photo=_get_photo(),
                caption=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            _cache(sent)


def fmt(val: float) -> str:
    s = f"{val:,.10f}".rstrip("0")
    return s if not s.endswith(".") else s + "0"


async def bot_send_msg(bot: Bot, chat_id: int, text: str, reply_markup=None) -> Message:
    if not _has_photo():
        return await bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    sent = await bot.send_photo(
        chat_id=chat_id,
        photo=_get_photo(),
        caption=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )
    _cache(sent)
    return sent
