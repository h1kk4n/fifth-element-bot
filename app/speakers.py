from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app import dp
from app.admin_panel.permissions import check_auth
from app.database.models import Speaker
from app.database.db import Session


speakers_buttons = {
    'show': 'show_speaker',
    'back': 'speakers_back'
}


def exact_speaker(update, context):
    session = Session()
    query = update.callback_query
    chat_id = query.message.chat_id,
    message_id = query.message.message_id

    speaker_id = int(query.data.replace(speakers_buttons['show'], ''))

    speaker = session.query(Speaker).filter(Speaker.id == speaker_id).first()

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Назад', callback_data=speakers_buttons['back'])]]
    )

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=str(speaker),
        reply_markup=keyboard
    )
    session.close()


def show_speakers(update, context):
    session = Session()
    speakers = session.query(Speaker).all()
    session.close()

    query = update.callback_query
    if query is not None:
        update = query

    speakers_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                text=speaker.name,
                callback_data=f'{speakers_buttons["show"]} {speaker.id}')
             ] for speaker in speakers
        ]
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Список спикеров',
        reply_markup=speakers_keyboard
    )


dp.add_handler(CommandHandler(command='speakers', callback=show_speakers))
dp.add_handler(CallbackQueryHandler(pattern=speakers_buttons['show'], callback=exact_speaker))
dp.add_handler(CallbackQueryHandler(pattern=speakers_buttons['back'], callback=show_speakers))
