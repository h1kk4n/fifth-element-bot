from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from app import dp
from app.database.models import User
from app.database.db import Session
from app.admin_panel.permissions import check_auth


AUTH_CODE = 1


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


def show_all_participants(update, context):
    session = Session()
    users = session.query(User).all()
    users_list = '<b><i>Список участников</i></b>:\n' + '\n'.join(
        f"№{user.id} {user.surname} {user.name} {user.patronymic} - {user.score} PTS" for user in users
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=users_list
    )
    session.close()


dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler(command='login', callback=auth_start)],
    states={
        AUTH_CODE: [MessageHandler(filters=Filters.text, callback=auth_complete)]
    },
    fallbacks=[]
))
dp.add_handler(CommandHandler(command='profile', callback=show_profile))
dp.add_handler(CommandHandler(command='score', callback=show_all_participants))
