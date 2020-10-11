from telegram.ext import CommandHandler

from app import dp
from app.database.models import User
from app.database.db import Session
from config import Config


def show_start_or_help(update, context):
    bot_message = """Привет\n
/help - Вот это же сообщение
/login - Авторизация для участников
/speakers - Посмотреть спикеров
/program - Информация о программах на разные дни
/score - Общий счет\n
"""

    session = Session()
    user_id = update.message.chat_id

    user = session.query(User).filter(user_id == User.tg_chat_id).first()
    session.close()
    if user:
        bot_message += """<i>Для участников</i>:
/profile - Личный счет
/code - Сдать код\n
"""
    if user_id == Config.TG_OWNER_ID or user_id == Config.SHISHI_ID:
        bot_message += """<b><i>Админ-панель</i></b>:
Добавить:
/addcode - код
/adduser - участника
/addspeaker - спикера
/addprogram - день программы
Удалить:
/delcode - код
/deluser - участника
/delspeaker - спикера
/delprogram - день программы
Просмотреть:
/viewcodes - список кодов
/viewusers - список участников
/viewspeakers - список спикеров
/viewprogram - существующие дни программы
Сбросить полностью таблицу
/dropcodes - кодов
/dropusers - участников
/dropspeakers - спикеров
/dropprogram - программы"""

    context.bot.send_message(
        chat_id=user_id,
        text=bot_message
    )


dp.add_handler(CommandHandler(command=['start', 'help'], callback=show_start_or_help))