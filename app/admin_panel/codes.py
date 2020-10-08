from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from config import Config
from app.database.db import Session, engine
from app.database.models import Code, Base
from app import dp


CODE_ADD_VALUE, CODE_ADD_COST, CODE_REMOVE_ID = range(3)


# View codes
def view_codes(update, context):
    session = Session()

    codes = session.query(Code).all()

    codes_list = '<b><i>Список действительных кодов</i></b>:\n' + '\n'.join(str(code) for code in codes)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=codes_list
    )


# Delete all codes
def drop_codes(update, context):
    Base.metadata.tables['codes'].drop(bind=engine)
    Base.metadata.tables['codes'].create(bind=engine)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Таблица кодов сброшена'
    )


# Add code
def code_add_start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите сам код'
    )
    return CODE_ADD_VALUE


def code_add_value(update, context):
    context.user_data['value'] = update.message.text

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите, сколько пользователь получит за ввод данного кода'
    )
    return CODE_ADD_COST


def code_add_done(update, context):
    session = Session()

    context.user_data['cost'] = int(update.message.text)

    rows = session.query(Code).count()

    code = Code(
        id=rows + 1,
        value=context.user_data.get('value', None),
        cost=context.user_data.get('cost', None)
    )

    context.user_data.pop('value', None)
    context.user_data.pop('cost', None)

    session.add(code)
    session.commit()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Код добавлен'
    )

    session.close()

    return ConversationHandler.END


# Remove code
def code_remove_start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите номер кода из списка кодов'
    )
    return CODE_REMOVE_ID


def code_remove_id(update, context):
    session = Session()

    code_id = int(update.message.text)

    code = session.query(Code).filter(Code.id == code_id).first()

    session.delete(code)
    session.commit()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Код удален'
    )


dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='addcode', callback=code_add_start),
        CommandHandler(command='delcode', callback=code_remove_start)
    ],
    states={
        CODE_ADD_VALUE: [MessageHandler(Filters.text, callback=code_add_value)],
        CODE_ADD_COST: [MessageHandler(Filters.text, callback=code_add_done)],
        CODE_REMOVE_ID: [MessageHandler(Filters.text, callback=code_remove_id)]
    },
    fallbacks=[]
))
dp.add_handler(CommandHandler='viewcodes', callback=view_codes)
dp.add_handler(CommandHandler='dropcodes', callback=drop_codes)


if __name__ == '__main__':
    pass
