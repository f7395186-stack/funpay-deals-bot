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


async def _self_ping_loop():
    """On Render, the free Web Service instance type spins down after ~15
    minutes without incoming HTTP traffic. Render sets RENDER_EXTERNAL_URL
    automatically for web services -- if present, we periodically make a
    real HTTP request to our own public URL so the service always looks
    active, with no external ping service (cron-job.org/UptimeRobot) needed.
    """
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return
    from aiohttp import ClientSession, ClientTimeout
    async with ClientSession(timeout=ClientTimeout(total=15)) as session:
        while True:
            await asyncio.sleep(600)  # every 10 minutes
            try:
                async with session.get(url) as resp:
                    logging.info(f"Self-ping {url} -> {resp.status}")
            except Exception as e:
                logging.warning(f"Self-ping failed: {e}")


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
    asyncio.create_task(_self_ping_loop())
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
