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
    length = 12
    auth_code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
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
        user_id = session.query(User).count() + 1

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

if __name__ == '__main__':
 """   session = Session()
    users = '''Волошина Полина Андреевна
Бакеева Полина Евгеньевна
Максимова Мария Игоревна
Кияненко Елизавета Александровна
Реутин Антон Викторович
Машкова Алисия Валерьевна
Петренко Елизавета Владимировна
Соломатина Аксинья Сергеевна
Панченко Даниил Александрович
Головань Владимир Олегович
Папкова Анастасия Сергеевна
Терещенко Екатерина Александовна
Хаценко Елена Александровна
Татаренко Александр Олегович
Соколова Юлия Андреевна
Абрамова Анастаия Евгеньевна
Годунова Алина Сергеевна
Абраменко Дмитрий Дмитриевич
Долбня лександр Алексндрович
Цыцура Дарина Игоревна
Королев Илья Андреевич
Татюк Алина Сергеевна
Широкая Екатерина Витальевна
Гортунова Виктория Александровна
Дуброва Дарья Евгеньевна
Ефимако Анастасия Андреевна
Tangyan Lendrush Sosovich
Елистратов Алексей Владимирович
Гурченко Екатерина .
Минина Мария .'''.split('\n')
    for some in users:
        user_id_ = session.query(User).count() + 1
        surname, name, patr = some.split()
        user = User(
            id=user_id_,
            surname=surname,
            name=name,
            patronymic=patr,
            auth_code=make_auth_code()
        )
        session.add(user)
    session.commit()
    session.close()"""
