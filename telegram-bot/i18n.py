"""Minimal i18n layer: two supported languages, ru (default) and en.

Every user-facing message the *acting* user sees (menus, deal flow, balance,
requisites, referrals, FAQ, support) is looked up here by key and rendered in
that user's own stored language preference (users.lang in the DB).

Messages sent TO THE BOT OWNER/ADMIN (notifications about new users, new
deals, withdrawal requests, etc.) are intentionally left hardcoded in
Russian in the handler files -- the admin is a fixed single person, not an
end user, so they don't need translation.

When a message is sent to a *different* user than the one who triggered the
action (e.g. notifying the seller that a deal was paid), always look up
THAT recipient's own language via db.get_lang(recipient_id) -- never reuse
the acting user's language for someone else's notification.
"""

LANGS = ("ru", "en")
DEFAULT_LANG = "ru"


def norm_lang(lang: str | None) -> str:
    return lang if lang in LANGS else DEFAULT_LANG


BTN = {
    "main_menu":        {"ru": "🏠 Главное меню",              "en": "🏠 Main menu"},
    "create_deal":      {"ru": "🤝 Создать сделку",             "en": "🤝 Create deal"},
    "balance":          {"ru": "💰 Баланс",                     "en": "💰 Balance"},
    "requisites":       {"ru": "👛 Реквизиты",                  "en": "👛 Requisites"},
    "referrals":        {"ru": "🎁 Рефералы",                   "en": "🎁 Referrals"},
    "faq":              {"ru": "💎 F.A.Q",                      "en": "💎 F.A.Q"},
    "web_market":       {"ru": "🌐 WEB маркет",                 "en": "🌐 WEB market"},
    "support":          {"ru": "⚡ Поддержка",                  "en": "⚡ Support"},
    "language":         {"ru": "🌍 Язык / Language",            "en": "🌍 Язык / Language"},
    "role_buyer":       {"ru": "🛒 Я — Покупатель",             "en": "🛒 I'm a Buyer"},
    "role_seller":      {"ru": "💼 Я — Продавец",               "en": "💼 I'm a Seller"},
    "cancel":           {"ru": "❌ Отмена",                     "en": "❌ Cancel"},
    "link_requisites":  {"ru": "👛 Привязать реквизиты",        "en": "👛 Link requisites"},
    "pay_deal":         {"ru": "💳 Оплатить сделку",            "en": "💳 Pay for deal"},
    "confirm_receipt":  {"ru": "✅ Подтвердить получение товара", "en": "✅ Confirm receipt of goods"},
    "deposit":          {"ru": "➕ Пополнить",                  "en": "➕ Deposit"},
    "withdraw":         {"ru": "💸 Вывести",                    "en": "💸 Withdraw"},
    "edit_card":        {"ru": "💳 Изменить карту",             "en": "💳 Change card"},
    "edit_crypto":      {"ru": "🪙 Изменить крипту",            "en": "🪙 Change crypto"},
    "edit_wallet":      {"ru": "👛 Изменить кошелёк",           "en": "👛 Change wallet"},
    "edit_stars":       {"ru": "⭐ Юзернейм для Stars",         "en": "⭐ Username for Stars"},
    "share_link":       {"ru": "📤 Поделиться ссылкой",         "en": "📤 Share link"},
    "lang_ru":          {"ru": "🇷🇺 Русский",                   "en": "🇷🇺 Русский"},
    "lang_en":          {"ru": "🇬🇧 English",                   "en": "🇬🇧 English"},
}


def b(lang: str, key: str) -> str:
    return BTN[key][norm_lang(lang)]


TEXTS = {
    "welcome": {
        "ru": "{star} <b>Добро пожаловать в Funpay Deals Bot</b> — ваш надёжный сервис "
              "безопасных сделок! {shield}\n\n{lightning} Автоматизированные сделки\n"
              "{diamond} Поддержка 7 валют\n{chart} Реферальная система\n"
              "{wallet} Вывод в любой валюте\n{clock24} Поддержка 24/7\n\n"
              "{handshake} <b>Выберите раздел ниже!</b>",
        "en": "{star} <b>Welcome to Funpay Deals Bot</b> — your trusted secure escrow "
              "service! {shield}\n\n{lightning} Automated deals\n"
              "{diamond} Support for 7 currencies\n{chart} Referral system\n"
              "{wallet} Withdraw in any currency\n{clock24} 24/7 support\n\n"
              "{handshake} <b>Choose a section below!</b>",
    },
    "faq": {
        "ru": "{shield} <b>F.A.Q — Часто задаваемые вопросы</b>\n\n"
              "{check} <b>Как работает гарант?</b>\nПокупатель платит — деньги "
              "замораживаются. Продавец передаёт товар через @Funpay_Support_Deals. "
              "После подтверждения — деньги у продавца.\n\n"
              "{dollar} <b>Комиссия:</b> 5%\n\n"
              "{star} <b>Валюты:</b> Stars · USDT · TON · RUB · BYN · KZT · UZS\n\n"
              "{wallet} <b>Вывод:</b> «Баланс» → «Вывести»\n\n"
              "{phone} Поддержка: <b>{support}</b>",
        "en": "{shield} <b>F.A.Q — Frequently Asked Questions</b>\n\n"
              "{check} <b>How does the escrow work?</b>\nThe buyer pays — the money "
              "is frozen. The seller delivers the item via @Funpay_Support_Deals. "
              "Once confirmed, the money goes to the seller.\n\n"
              "{dollar} <b>Commission:</b> 5%\n\n"
              "{star} <b>Currencies:</b> Stars · USDT · TON · RUB · BYN · KZT · UZS\n\n"
              "{wallet} <b>Withdrawal:</b> \"Balance\" → \"Withdraw\"\n\n"
              "{phone} Support: <b>{support}</b>",
    },
    "support": {
        "ru": "{gear} <b>Поддержка Funpay Deals</b>\n\n{phone} Аккаунт: <b>{support}</b>\n\n"
              "{clock} Время ответа: до 15 минут\n{shield} Работаем 24/7 без выходных.",
        "en": "{gear} <b>Funpay Deals Support</b>\n\n{phone} Account: <b>{support}</b>\n\n"
              "{clock} Response time: up to 15 minutes\n{shield} We work 24/7, no days off.",
    },
    "deal_role_prompt": {
        "ru": "{handshake} <b>Создание сделки</b>\n\n{question} Кем вы выступаете в этой сделке?",
        "en": "{handshake} <b>Create a deal</b>\n\n{question} What is your role in this deal?",
    },
    "deal_no_requisites": {
        "ru": "{imp1}{imp2}{imp3} <b>Ошибка: не привязаны реквизиты!</b>\n\n"
              "{shield} Мы должны знать, куда переводить деньги.\n"
              "{key} Привяжите реквизиты прямо сейчас.",
        "en": "{imp1}{imp2}{imp3} <b>Error: no requisites linked!</b>\n\n"
              "{shield} We need to know where to send your money.\n"
              "{key} Link your requisites right now.",
    },
    "deal_choose_currency": {
        "ru": "{dollar} <b>Шаг 1 из 3 — Выберите валюту:</b>\n\n"
              "{star} Stars · {diamond} TON · {dollar} USDT · 🇷🇺 RUB · 🇧🇾 BYN · 🇰🇿 KZT · 🇺🇿 UZS · 🇺🇦 UAH",
        "en": "{dollar} <b>Step 1 of 3 — Choose a currency:</b>\n\n"
              "{star} Stars · {diamond} TON · {dollar} USDT · 🇷🇺 RUB · 🇧🇾 BYN · 🇰🇿 KZT · 🇺🇿 UZS · 🇺🇦 UAH",
    },
    "deal_enter_amount": {
        "ru": "{calc} <b>Шаг 2 из 3 — Введите сумму</b>\n\n{timer} Валюта: {sym} <b>{currency}</b>\n\n"
              "{pencil} Введите число, например: <code>500</code>",
        "en": "{calc} <b>Step 2 of 3 — Enter the amount</b>\n\n{timer} Currency: {sym} <b>{currency}</b>\n\n"
              "{pencil} Enter a number, e.g.: <code>500</code>",
    },
    "deal_amount_error": {
        "ru": "{cross} <b>Ошибка:</b> Введите число больше нуля.",
        "en": "{cross} <b>Error:</b> Enter a number greater than zero.",
    },
    "deal_enter_description": {
        "ru": "{notepad} <b>Шаг 3 из 3 — Опишите товар / услугу</b>\n\n"
              "{pencil} Пример: <i>Аккаунт Minecraft Premium, 2024</i>",
        "en": "{notepad} <b>Step 3 of 3 — Describe the item / service</b>\n\n"
              "{pencil} Example: <i>Minecraft Premium account, 2024</i>",
    },
    "deal_desc_too_short": {
        "ru": "{cross} Описание слишком короткое. Минимум 3 символа.",
        "en": "{cross} Description too short. Minimum 3 characters.",
    },
    "deal_created": {
        "ru": "{verified} <b>Сделка создана!</b>\n\n{grid} <b>ID:</b> <code>{did}</code>\n"
              "{dollar} <b>Сумма:</b> {sym} {amount} {currency}\n"
              "{briefcase} <b>Описание:</b> {desc}\n{clock} <b>Статус:</b> Ожидание оплаты\n\n"
              "{lightning} <b>Ссылка для покупателя:</b>\n<code>{link}</code>\n\n"
              "{shield} Отправьте эту ссылку покупателю.",
        "en": "{verified} <b>Deal created!</b>\n\n{grid} <b>ID:</b> <code>{did}</code>\n"
              "{dollar} <b>Amount:</b> {sym} {amount} {currency}\n"
              "{briefcase} <b>Description:</b> {desc}\n{clock} <b>Status:</b> Awaiting payment\n\n"
              "{lightning} <b>Link for the buyer:</b>\n<code>{link}</code>\n\n"
              "{shield} Send this link to the buyer.",
    },
    "deal_not_found": {
        "ru": "{cross} Сделка не найдена.",
        "en": "{cross} Deal not found.",
    },
    "deal_unavailable": {
        "ru": "{cross} Сделка недоступна (статус: {status}).",
        "en": "{cross} Deal unavailable (status: {status}).",
    },
    "deal_payment_prompt": {
        "ru": "{shield} <b>Сделка #{deal_id}</b>\n\n{briefcase} <b>Описание:</b> {desc}\n"
              "{dollar} <b>Сумма:</b> {sym} {amount} {currency}\n{clock} <b>Статус:</b> Ожидание оплаты\n\n"
              "{handshake} Нажмите кнопку ниже для оплаты.",
        "en": "{shield} <b>Deal #{deal_id}</b>\n\n{briefcase} <b>Description:</b> {desc}\n"
              "{dollar} <b>Amount:</b> {sym} {amount} {currency}\n{clock} <b>Status:</b> Awaiting payment\n\n"
              "{handshake} Tap the button below to pay.",
    },
    "alert_deal_not_found": {"ru": "❌ Сделка не найдена.", "en": "❌ Deal not found."},
    "alert_deal_already_paid": {"ru": "❌ Сделка уже оплачена.", "en": "❌ Deal already paid."},
    "alert_cant_pay_own": {"ru": "❌ Нельзя оплатить свою сделку.", "en": "❌ You can't pay for your own deal."},
    "alert_payment_success": {"ru": "✅ Оплата прошла!", "en": "✅ Payment successful!"},
    "alert_cant_confirm_stage": {
        "ru": "❌ Сделку нельзя подтвердить на этом этапе.",
        "en": "❌ This deal can't be confirmed at this stage.",
    },
    "alert_only_buyer_confirm": {
        "ru": "❌ Подтвердить может только покупатель.",
        "en": "❌ Only the buyer can confirm this.",
    },
    "alert_deal_completed": {"ru": "✅ Сделка завершена!", "en": "✅ Deal completed!"},
    "alert_no_funds_in": {"ru": "❌ У вас нет средств в {currency}.", "en": "❌ You have no funds in {currency}."},
    "deal_payment_accepted": {
        "ru": "{verified} <b>Оплата принята!</b>\n\n{shield} {sym} {amount} {currency} заморожено.\n\n"
              "{clock} Ожидайте, пока продавец передаст товар через <b>{support}</b>",
        "en": "{verified} <b>Payment accepted!</b>\n\n{shield} {sym} {amount} {currency} has been frozen.\n\n"
              "{clock} Wait for the seller to deliver the item via <b>{support}</b>",
    },
    "deal_paid_notify_seller": {
        "ru": "{moneybag} <b>Сделка #{deal_id} оплачена!</b>\n\n"
              "{shield} Деньги ({sym} {amount} {currency}) заморожены.\n\n"
              "{imp1}{imp2}{imp3} <b>ВНИМАНИЕ!</b>\nПередавайте товар <b>ТОЛЬКО</b> через <b>{support}</b>\n\n"
              "{cross} Напрямую покупателю — сделка аннулируется!",
        "en": "{moneybag} <b>Deal #{deal_id} has been paid!</b>\n\n"
              "{shield} The funds ({sym} {amount} {currency}) are frozen.\n\n"
              "{imp1}{imp2}{imp3} <b>ATTENTION!</b>\nDeliver the item <b>ONLY</b> via <b>{support}</b>\n\n"
              "{cross} Delivering directly to the buyer will void the deal!",
    },
    "deal_completed_buyer": {
        "ru": "{verified} <b>Сделка #{deal_id} завершена!</b>\n\n{shield} Спасибо, что пользуетесь Funpay Deals.\n"
              "{chart} Продавцу зачислено {sym} {payout} {currency} (комиссия {commission_pct}%).",
        "en": "{verified} <b>Deal #{deal_id} completed!</b>\n\n{shield} Thanks for using Funpay Deals.\n"
              "{chart} The seller received {sym} {payout} {currency} (commission {commission_pct}%).",
    },
    "deal_completed_notify_seller": {
        "ru": "{moneybag} <b>Сделка #{deal_id} завершена!</b>\n\n{check} Покупатель подтвердил получение товара.\n"
              "{dollar} На баланс зачислено: {sym} {payout} {currency}\n\n"
              "{wallet} Вывести средства можно в разделе «Баланс».",
        "en": "{moneybag} <b>Deal #{deal_id} completed!</b>\n\n{check} The buyer confirmed receipt of the item.\n"
              "{dollar} Credited to your balance: {sym} {payout} {currency}\n\n"
              "{wallet} You can withdraw funds in the \"Balance\" section.",
    },
    "balance_header": {"ru": "{wallet} <b>Ваш баланс</b>\n", "en": "{wallet} <b>Your balance</b>\n"},
    "balance_id_line": {"ru": "{key} Ваш ID: <code>{uid}</code>\n", "en": "{key} Your ID: <code>{uid}</code>\n"},
    "add_format_error": {
        "ru": "{cross} Формат: <code>/add id сумма валюта</code>\nНапример: <code>/add 123456789 100 USDT</code>",
        "en": "{cross} Format: <code>/add id amount currency</code>\nExample: <code>/add 123456789 100 USDT</code>",
    },
    "add_invalid_data": {
        "ru": "{cross} Некорректные данные. Валюты: {currencies}",
        "en": "{cross} Invalid data. Currencies: {currencies}",
    },
    "add_credited_to_invoker": {
        "ru": "{verified} <b>Начислено!</b>\n\n{dollar} {sym} {amount} {currency} зачислено на ID <code>{target_id}</code>",
        "en": "{verified} <b>Credited!</b>\n\n{dollar} {sym} {amount} {currency} credited to ID <code>{target_id}</code>",
    },
    "balance_topped_up_notify": {
        "ru": "{moneybag} <b>Баланс пополнен!</b>\n\n{dollar} +{sym} {amount} {currency}",
        "en": "{moneybag} <b>Your balance has been topped up!</b>\n\n{dollar} +{sym} {amount} {currency}",
    },
    "deposit_text": {
        "ru": "{moneybag} <b>Пополнение баланса</b>\n\n"
              "{notepad} Пополнение проходит через оператора, чтобы гарантировать безопасность средств.\n\n"
              "{phone} Напишите в поддержку <b>{support}</b> и укажите:\n— сумму и валюту пополнения\n"
              "— ваш ID: <code>{uid}</code>\n\n{clock} Баланс будет зачислен после подтверждения оплаты.",
        "en": "{moneybag} <b>Top up balance</b>\n\n"
              "{notepad} Top-ups go through an operator to guarantee the safety of your funds.\n\n"
              "{phone} Message support <b>{support}</b> and provide:\n— the amount and currency\n"
              "— your ID: <code>{uid}</code>\n\n{clock} Your balance will be credited once payment is confirmed.",
    },
    "withdraw_choose_currency": {
        "ru": "{calc} <b>Вывод средств — выберите валюту:</b>",
        "en": "{calc} <b>Withdraw funds — choose a currency:</b>",
    },
    "withdraw_enter_amount": {
        "ru": "{calc} <b>Введите сумму вывода</b>\n\n{wallet} Доступно: {sym} {available} {currency}\n\n"
              "{pencil} Введите число, например: <code>100</code>",
        "en": "{calc} <b>Enter the withdrawal amount</b>\n\n{wallet} Available: {sym} {available} {currency}\n\n"
              "{pencil} Enter a number, e.g.: <code>100</code>",
    },
    "withdraw_amount_error": {
        "ru": "{cross} <b>Ошибка:</b> введите число от 0 до {available} {currency}.",
        "en": "{cross} <b>Error:</b> enter a number from 0 to {available} {currency}.",
    },
    "withdraw_enter_requisite": {
        "ru": "{key} <b>Укажите реквизит для вывода</b>\n\n"
              "{pencil} Введите карту, кошелёк или username, куда вывести {sym} {amount} {currency}.",
        "en": "{key} <b>Enter the payout requisite</b>\n\n"
              "{pencil} Enter the card, wallet or username to withdraw {sym} {amount} {currency} to.",
    },
    "withdraw_requisite_short": {
        "ru": "{cross} Реквизит слишком короткий.",
        "en": "{cross} Requisite is too short.",
    },
    "withdraw_insufficient_funds": {
        "ru": "{cross} Недостаточно средств.",
        "en": "{cross} Insufficient funds.",
    },
    "withdraw_created": {
        "ru": "{verified} <b>Заявка на вывод создана!</b>\n\n{grid} <b>ID заявки:</b> <code>{withdraw_id}</code>\n"
              "{dollar} <b>Сумма:</b> {sym} {amount} {currency}\n{key} <b>Реквизит:</b> <code>{requisite}</code>\n\n"
              "{clock} Выплата обрабатывается вручную, обычно в течение 24 часов.",
        "en": "{verified} <b>Withdrawal request created!</b>\n\n{grid} <b>Request ID:</b> <code>{withdraw_id}</code>\n"
              "{dollar} <b>Amount:</b> {sym} {amount} {currency}\n{key} <b>Requisite:</b> <code>{requisite}</code>\n\n"
              "{clock} Payout is processed manually, usually within 24 hours.",
    },
    "requisites_text": {
        "ru": "{key} <b>Ваши реквизиты</b>\n\n{card} Карта: <code>{card_val}</code>\n"
              "{bitcoin} Крипта: <code>{crypto_val}</code>\n{wallet} Кошелёк: <code>{wallet_val}</code>\n"
              "{star} Stars username: <code>{stars_val}</code>\n\n{pencil} Выберите, что изменить:",
        "en": "{key} <b>Your requisites</b>\n\n{card} Card: <code>{card_val}</code>\n"
              "{bitcoin} Crypto: <code>{crypto_val}</code>\n{wallet} Wallet: <code>{wallet_val}</code>\n"
              "{star} Stars username: <code>{stars_val}</code>\n\n{pencil} Choose what to edit:",
    },
    "not_set": {"ru": "не указано", "en": "not set"},
    "prompt_edit_card": {"ru": "{card} Введите номер карты:", "en": "{card} Enter your card number:"},
    "prompt_edit_crypto": {
        "ru": "{bitcoin} Введите адрес криптокошелька:",
        "en": "{bitcoin} Enter your crypto wallet address:",
    },
    "prompt_edit_wallet": {
        "ru": "{wallet} Введите номер/адрес электронного кошелька:",
        "en": "{wallet} Enter your e-wallet number/address:",
    },
    "prompt_edit_stars": {
        "ru": "{star} Введите ваш username для получения Stars (например @username):",
        "en": "{star} Enter your username to receive Stars (e.g. @username):",
    },
    "requisite_too_short": {
        "ru": "{cross} Значение слишком короткое, минимум 3 символа.",
        "en": "{cross} Value too short, minimum 3 characters.",
    },
    "requisite_saved": {
        "ru": "{verified} <b>Реквизит сохранён!</b>\n\n{check} <code>{value}</code>",
        "en": "{verified} <b>Requisite saved!</b>\n\n{check} <code>{value}</code>",
    },
    "referrals_text": {
        "ru": "{gift} <b>Реферальная программа</b>\n\n{people} Приглашено друзей: <b>{count}</b>\n\n"
              "{lightning} Ваша реферальная ссылка:\n<code>{link}</code>\n\n"
              "{star} Делитесь ссылкой — приглашённые друзья закрепляются за вами навсегда.",
        "en": "{gift} <b>Referral program</b>\n\n{people} Friends invited: <b>{count}</b>\n\n"
              "{lightning} Your referral link:\n<code>{link}</code>\n\n"
              "{star} Share the link — friends you invite are permanently tied to you.",
    },
    "lang_menu_text": {
        "ru": "🌍 <b>Выберите язык / Choose your language</b>",
        "en": "🌍 <b>Выберите язык / Choose your language</b>",
    },
    "lang_set_ru": {"ru": "✅ Язык переключён на русский", "en": "✅ Язык переключён на русский"},
    "lang_set_en": {"ru": "✅ Language switched to English", "en": "✅ Language switched to English"},
}


def t(lang: str, text_key: str, **kwargs) -> str:
    template = TEXTS[text_key][norm_lang(lang)]
    return template.format(**kwargs) if kwargs else template
