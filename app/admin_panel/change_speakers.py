from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from app import dp
from app.admin_panel.permissions import check_permissions
from app.database.models import Speaker, Base
from app.database.db import Session, engine

SPEAKER_NAME, SPEAKER_DESCRIPTION, SPEAKER_REMOVE = range(3)


# View speakers
def view_speakers(update, context):
    if check_permissions(update, context):
        session = Session()

        speakers = session.query(Speaker).all()

        speakers_list = '<b><i>Список спикеров</i></b>:\n' + '\n'.join(
            f"№{speaker.id} {speaker.surname} {speaker.name} {speaker.patronymic}" for speaker in speakers
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=speakers_list
        )
        session.close()


# Drop speakers
def drop_speakers(update, context):
    if check_permissions(update, context):
        Base.metadata.tables['speakers'].drop(bind=engine)
        Base.metadata.tables['speakers'].create(bind=engine)

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Таблица спикеров сброшена'
        )


# Add speaker
def speaker_add_name(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите ФИО спикера в формате "Фамилия Имя Отчество"'
        )
        return SPEAKER_NAME
    else:
        return ConversationHandler.END


def speaker_add_description(update, context):
    try:
        context.user_data['surname'], \
         context.user_data['name'], \
         context.user_data['patronymic'] = update.message.text.strip().split()
    except (ValueError, IndexError):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Произошла ошибка, попробуйте ввести ФИО спикера повторно'
        )
        return SPEAKER_NAME
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите введите описание для спикера"'
        )
        return SPEAKER_DESCRIPTION


def speaker_add_complete(update, context):
    session = Session()

    speaker_id = session.query(Speaker).count() + 1
    surname = context.user_data['surname']
    name = context.user_data['name']
    patronymic = context.user_data['patronymic']
    description = update.message.text

    speaker = Speaker(
        id=speaker_id,
        surname=surname,
        name=name,
        patronymic=patronymic,
        description=description
    )

    session.add(speaker)
    session.commit()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Спикер добавлен'
    )

    session.close()
    del context.user_data['surname']
    del context.user_data['name']
    del context.user_data['patronymic']
    return ConversationHandler.END


# Remove speaker
def speaker_remove_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите номер спикера из списка'
        )
        return SPEAKER_REMOVE
    else:
        return ConversationHandler.END


def speaker_remove_complete(update, context):
    session = Session()
    try:
        speaker_id = int(update.message.text)
        speaker = session.query(Speaker).filter(Speaker.id == speaker_id).first()

        if speaker:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Спикер удален'
            )

            session.delete(speaker)
            session.commit()
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Спикера под таким номером нет'
            )
    except ValueError:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Что-то пошло не так, попробуйте ввести команду повторно'
        )
    finally:
        session.close()
        return ConversationHandler.END


dp.add_handler(CommandHandler(command='viewspeakers', callback=view_speakers))
dp.add_handler(CommandHandler(command='dropspeakers', callback=drop_speakers))
dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='addspeaker', callback=speaker_add_name),
        CommandHandler(command='delspeaker', callback=speaker_remove_start)
    ],
    states={
        SPEAKER_NAME: [MessageHandler(filters=Filters.text, callback=speaker_add_description)],
        SPEAKER_DESCRIPTION: [MessageHandler(filters=Filters.text, callback=speaker_add_complete)],
        SPEAKER_REMOVE: [MessageHandler(filters=Filters.text, callback=speaker_remove_complete)]
    },
    fallbacks=[]
))