# Funpay Deals Bot

Telegram-бот на aiogram 3 для безопасных сделок (эскроу): создание сделки,
оплата, подтверждение, вывод средств, реферальная программа, админ-панель.

## Запуск локально / на Replit

```
pip install -r requirements.txt
BOT_TOKEN=... python main.py
```

## Деплой на Render.com (бесплатно, шаг за шагом)

1. **GitHub:** запушьте этот репозиторий на GitHub (через Git-панель Replit,
   один раз подключив свой GitHub-аккаунт — токен вводить нигде не нужно).
2. **Render:** зайдите на https://render.com и зарегистрируйтесь через GitHub.
3. Нажмите **New → Web Service**, выберите ваш репозиторий.
4. Настройки сервиса:
   - **Root Directory:** `telegram-bot`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** Free
5. В разделе **Environment** добавьте переменную `BOT_TOKEN` со значением
   токена от @BotFather (это делается прямо в интерфейсе Render, никому
   больше передавать токен не нужно).
6. Нажмите **Create Web Service** — Render соберёт и запустит бота.
   `main.py` сам поднимает маленький HTTP-сервер на порту из `PORT`
   (Render его туда передаёт), чтобы Render видел сервис как "живой".

### Важно: бесплатный тариф Render засыпает

Free Web Service на Render "засыпает" после ~15 минут без входящих HTTP-
запросов. Сам бот (long polling к Telegram) не считается таким запросом,
поэтому раз в 5-10 минут нужно, чтобы кто-то или что-то дергало URL вашего
сервиса на Render (Render выдаст его в духе `https://ваш-сервис.onrender.com`).

Бесплатный способ не спать: зарегистрируйтесь на https://cron-job.org или
https://uptimerobot.com и настройте пинг GET-запросом на ваш Render URL
каждые 5-10 минут. Тогда бот будет работать постоянно бесплатно.
