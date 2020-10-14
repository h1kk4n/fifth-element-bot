from telegram.ext import MessageHandler, ConversationHandler, CommandHandler
from telegram.ext import Filters

from app import dp
from app.database.models import User
from app.database.db import Session
from config import Config

SEND_ALL = range(1)


def check_permissions(update, context):
    session = Session()
    user_id = update.message.chat_id

    session.close()
    if user_id == Config.TG_OWNER_ID or user_id == Config.SHISHI_ID:
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


def send_all_message(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите текст рассылки'
        )
        return SEND_ALL
    else:
        return ConversationHandler.END


def send_all(update, context):
    session = Session()

    bot_message = update.message.text
    users = session.query(User).all()

    for user in users:
        if user.tg_chat_id:
            context.bot.send_message(
                chat_id=user.tg_chat_id,
                text=bot_message
            )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Сообщение отправлено всем авторизованным участникам'
    )

    session.close()
    return ConversationHandler.END


def show_score(update, context):
    if check_permissions(update, context):
        session = Session()
        users = session.query(User).all()

        bot_message = '<b><i>Общий счет</i></b>\n\n-' + '\n-'.join(
            f"{user.surname} {user.name} {user.patronymic} - {user.score} PTS"
            for user in users
        )
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )


dp.add_handler(CommandHandler(command='score', callback=show_score))
dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler(command='sendall', callback=send_all_message)],
    states={
        SEND_ALL: [MessageHandler(filters=Filters.text, callback=send_all)]
    },
    fallbacks=[]
))