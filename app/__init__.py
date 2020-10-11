from telegram.ext import Updater, Defaults
from config import Config

updater = Updater(
    token=Config.BOT_TOKEN,
    defaults=Defaults(
        parse_mode="HTML",
        disable_web_page_preview=True
    ),
    use_context=True
)

dp = updater.dispatcher

from app import pass_codes, participants
from app.admin_panel import codes, users
