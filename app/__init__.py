from telegram.ext import Updater, Defaults
from config import Config

updater = Updater(
    token=Config.BOT_TOKEN,
    defaults=Defaults(
        parse_mode="HTML",
        disable_web_page_preview=1
    ),
    use_context=True
)

dp = updater.dispatcher
