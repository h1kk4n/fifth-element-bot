from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app import dp
from app.database.models import Program
from app.database.db import Session


program_buttons = {
    'show': 'show_day',
    'back': 'program_back',
}


def exact_day(update, context):
    session = Session()
    query = update.callback_query
    day_id = int(query.data.replace(program_buttons['show'], ''))
    day = str(session.query(Program).filter(Program.id == day_id).first())

    keyboard = [
        []
    ]
    first_day = session.query(Program).order_by(Program.id).first()
    last_day = session.query(Program).order_by(Program.id.desc()).first()
    if day_id != first_day.id:
        keyboard[0].append(InlineKeyboardButton(text='<-', callback_data=f"{program_buttons['show']} {day_id - 1}"))
    keyboard[0].append(InlineKeyboardButton(text='Все дни', callback_data=program_buttons['back']))
    if day_id != last_day.id:
        keyboard[0].append(InlineKeyboardButton(text='->', callback_data=f"{program_buttons['show']} {day_id + 1}"))

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=day,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    session.close()


def show_program(update, context):
    session = Session()
    query = update.callback_query

    days = session.query(Program).all()
    days_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=day.title, callback_data=f"{program_buttons['show']} {day.id}")]
            for day in days
        ]
    )

    if not query:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='<b><i>Программа мероприятия</i></b>:',
            reply_markup=days_keyboard
        )
    else:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text='<b><i>Программа мероприятия</i></b>:',
            reply_markup=days_keyboard
        )


dp.add_handler(CommandHandler(command='program', callback=show_program))
dp.add_handler(CallbackQueryHandler(pattern=program_buttons['show'], callback=exact_day))
dp.add_handler(CallbackQueryHandler(pattern=program_buttons['back'], callback=show_program))
