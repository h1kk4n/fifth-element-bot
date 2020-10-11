from app.database.models import Moderators, User
from app.database.db import Session
from config import Config


def check_permissions(update, context):
    session = Session()
    user_id = update.message.chat_id
    
    moderator = session.query(Moderators).filter(user_id == Moderators.tg_chat_id).first()
    session.close()
    if user_id == Config.TG_OWNER_ID or user_id == Config.SHISHI_ID or moderator:
        return True
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Для вас эта функция недоступна'
        )
        return False


def check_auth(update, context):
    session = Session()
    user_id = update.message.chat_id

    user = session.query(User).filter(user_id == User.tg_chat_id).first()
    session.close()
    if user:
        return True

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Вы не авторизованный пользователь'
        )
        return False
