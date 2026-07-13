---
    name: Telegram premium emoji cannot appear in inline keyboard buttons
    description: Bot API constraint relevant to any Telegram bot work involving custom/premium emoji and buttons
    ---

    Telegram Bot API's InlineKeyboardButton.text field only accepts a plain UTF-8 string -- it does not support
    message entities, so <tg-emoji> custom/premium emoji spans (which work fine in message text/captions with
    parse_mode=HTML) cannot be rendered inside button labels. This is true regardless of whether the bot owner
    account has Telegram Premium -- Premium affects who can see/send custom emoji in messages, not what the
    Button API accepts.

    **Why:** Confirmed while extending premium-emoji usage from message bodies to button labels for the
    "Funpay Deals Bot" aiogram project; button labels remain regular unicode emoji.

    **How to apply:** When a user asks for custom/premium animated emoji "in the buttons too", implement premium
    emoji in message text/captions (where it works) and tell the user plainly that buttons are a hard platform
    limitation -- don't silently drop the request or fake it with unicode lookalikes without saying so.
    