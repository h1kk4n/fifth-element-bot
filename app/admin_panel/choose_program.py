from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from app import dp
from app.database.models import Program, Base
from app.database.db import Session, engine
from app.admin_panel.permissions import check_permissions

PROGRAM_ADD_DAY, PROGRAM_ADD_DESCRIPTION, PROGRAM_REMOVE = range(3)


# View program
def view_program(update, context):
    if check_permissions(update, context):
        session = Session()

        program = session.query(Program).all()
        program_list = "<b><i>Дни программы</i></b>\n" + '\n'.join(
            [f"№{day.id} {day.title}" for day in program]
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=program_list
        )
        session.close()


# Drop program
def drop_program(update, context):
    if check_permissions(update, context):
        Base.metadata.tables['program'].drop(bind=engine)
        Base.metadata.tables['program'].create(bind=engine)

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Все дни программы сброшены'
        )


# Add program day
def program_add_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите заголовок дня программы'
        )
        return PROGRAM_ADD_DAY
    else:
        return ConversationHandler.END


def program_add_description(update, context):
    context.user_data['day_title'] = update.message.text
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите описание дня'
    )
    return PROGRAM_ADD_DESCRIPTION


def program_add_complete(update, context):
    session = Session()
    day_id = 1
    try:
        day_id = session.query(Program).order_by(Program.id.desc()).first().id + 1
    except:
        day_id = session.query(Program).count() + 1
    finally:
        title = context.user_data['day_title']
        description = update.message.text

        day = Program(
            id=day_id,
            title=title,
            description=description
        )
        session.add(day)
        session.commit()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='День добавлен в программу'
        )
        session.close()
        return ConversationHandler.END


# Remove program day
def program_remove_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите номер дня из списка'
        )
        return PROGRAM_REMOVE
    else:
        return ConversationHandler.END


def program_remove_complete(update, context):
    session = Session()
    try:
        day_id = int(update.message.text)

        day = session.query(Program).filter(Program.id == day_id).first()

        if day:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='День удален удален из программы'
            )

            session.delete(day)
            session.commit()
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='В программе нет дня под таким номером нет'
            )
    except ValueError:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Что-то пошло не так, попробуйте ввести команду повторно'
        )
    finally:
        session.close()
        return ConversationHandler.END


dp.add_handler(CommandHandler(command='viewprogram', callback=view_program))
dp.add_handler(CommandHandler(command='dropprogram', callback=drop_program))
dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='addprogram', callback=program_add_start),
        CommandHandler(command='delprogram', callback=program_remove_start)
    ],
    states={
        PROGRAM_ADD_DAY: [MessageHandler(filters=Filters.text, callback=program_add_description)],
        PROGRAM_ADD_DESCRIPTION: [MessageHandler(filters=Filters.text, callback=program_add_complete)],
        PROGRAM_REMOVE: [MessageHandler(filters=Filters.text, callback=program_remove_complete)]
    },
    fallbacks=[]
))
