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

from app import start_and_help, participants, speakers, program, pass_codes
from app.admin_panel import change_codes, change_users, change_speakers, choose_program, permissions
