from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from app import dp
from app.database.models import User
from app.database.db import Session
from app.admin_panel.permissions import check_auth
from config import Config


AUTH_CODE, IDEA = range(2)


def auth_start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите ваш код для аутентификации'
    )
    return AUTH_CODE


def auth_complete(update, context):
    auth_code = update.message.text
    session = Session()

    user = session.query(User).filter(User.auth_code == auth_code).first()
    if user:
        session.query(User).filter(User.auth_code == auth_code).update({User.tg_chat_id: update.message.chat_id})
        session.commit()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Вы <b>{user.surname} {user.name}</b>.\nАвторизация прошла успешно"
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Введен неверный аутентификационный код"
        )
    return ConversationHandler.END


def show_profile(update, context):
    if check_auth(update, context):
        session = Session()
        user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=str(user)
        )


def idea_start(update, context):
    if check_auth(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите вашу идею для проекта'
        )
        return IDEA
    else:
        return ConversationHandler.END


def idea_complete(update, context):
    session = Session()

    user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()

    bot_message = f"{user.name} {user.surname} пишет:\n\n"
    idea_text = update.message.text

    bot_message += idea_text
    context.bot.send_message(
        chat_id=Config.SHISHI_ID,
        text=bot_message
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Отличное начало!\nУдачи в работе'
    )
    return ConversationHandler.END


dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='login', callback=auth_start),
        CommandHandler(command='idea', callback=idea_start)
    ],
    states={
        AUTH_CODE: [MessageHandler(filters=Filters.text, callback=auth_complete)],
        IDEA: [MessageHandler(filters=Filters.text, callback=idea_complete)]
    },
    fallbacks=[]
))
dp.add_handler(CommandHandler(command='profile', callback=show_profile))
