import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUPPORT_USERNAME = "@Funpay_Support_Deals"
COMMISSION = 0.05
DB_PATH = os.path.join(os.path.dirname(__file__), "funpay_deals.db")
ADMIN_ID = 7908632313
FUNPAY_URL = "https://funpay.com"
