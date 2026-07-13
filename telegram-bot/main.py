import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from config import BOT_TOKEN
import database as db
from handlers import start, deals, balance, requisites, referrals, admin


async def _run_keepalive_server():
    """Tiny HTTP server so hosts like Render (which require a bound port for
    'Web Service' deployments) see the process as healthy. Telegram itself
    doesn't need this -- the bot talks to Telegram via long polling -- this
    is purely to satisfy the host's port-binding / health-check requirement.
    Only starts if a PORT env var is present (e.g. on Render); does nothing
    on plain Replit workflow runs.
    """
    port = os.environ.get("PORT")
    if not port:
        return
    app = web.Application()
    app.router.add_get("/", lambda _req: web.Response(text="Funpay Deals Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(port))
    await site.start()
    logging.info(f"Keep-alive HTTP server listening on port {port}")


async def main():
    if not BOT_TOKEN:
        logging.critical("BOT_TOKEN не задан!")
        return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    await db.init_db()
    await _run_keepalive_server()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(deals.router)
    dp.include_router(balance.router)
    dp.include_router(requisites.router)
    dp.include_router(referrals.router)
    logging.info("Funpay Deals Bot запущен...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
