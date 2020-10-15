from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters
import string
import random

from app import dp
from app.database.models import User, Base
from app.database.db import Session, engine
from app.admin_panel.permissions import check_permissions


USER_ADD, USER_REMOVE = range(2)


def make_auth_code():
    length = 8
    auth_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    return auth_code


# View users
def view_users(update, context):
    if check_permissions(update, context):
        session = Session()
        users = session.query(User).all()

        users_list = '<b><i>Список пользователей</i></b>:\n' + '\n'.join(
            f"№{user.id} {user.surname} {user.name} {user.patronymic} - {user.auth_code}" for user in users
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=users_list
        )
        session.close()


# Delete all users
def drop_users(update, context):
    if check_permissions(update, context):
        Base.metadata.tables['users'].drop(bind=engine)
        Base.metadata.tables['users'].create(bind=engine)

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Таблица пользователей сброшена'
        )


# Add user
def user_add_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите ФИО пользователя в формате "Фамилия Имя Отвество"'
        )
        return USER_ADD
    else:
        return ConversationHandler.END


def user_add_complete(update, context):
    try:
        surname, name, patronymic = update.message.text.strip().split()
    except (ValueError, IndexError):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='ФИО пользователя введено неверно, введите его повторно'
        )
        return USER_ADD
    else:
        session = Session()
        user_id = 1
        try:
            user_id = session.query(User).order_by(User.id.desc()).first().id + 1
        except:
            user_id = session.query(User).count() + 1
        finally:
            user = User(
                id=user_id,
                surname=surname,
                name=name,
                patronymic=patronymic,
                auth_code=make_auth_code()
            )
            session.add(user)
            session.commit()

            bot_message = f"Добавлен пользователь {user.surname} {user.name}.\nКод для аутентификации - {user.auth_code}"

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=bot_message
            )
            session.close()
            return ConversationHandler.END


# Remove user
def user_remove_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Для удаления пользователя введите его номер в списке'
        )
        return USER_REMOVE
    else:
        return ConversationHandler.END


def user_remove_complete(update, context):
    try:
        user_id = int(update.message.text)
    except ValueError:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введен некорректный номер, попробуйте еще раз'
        )
    else:
        session = Session()
        user = session.query(User).filter(User.id == user_id).first()

        if user:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f'Пользователь {user.surname} {user.name} удален'
            )

            session.delete(user)
            session.commit()
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Такого пользователя нет в базе'
            )
        session.close()
        return ConversationHandler.END


dp.add_handler(CommandHandler(command='viewusers', callback=view_users))
dp.add_handler(CommandHandler(command='dropusers', callback=drop_users))
dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='adduser', callback=user_add_start),
        CommandHandler(command='deluser', callback=user_remove_start)
    ],
    states={
        USER_ADD: [MessageHandler(filters=Filters.text, callback=user_add_complete)],
        USER_REMOVE: [MessageHandler(filters=Filters.text, callback=user_remove_complete)]
    },
    fallbacks=[]
))