from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from app import dp
from app.admin_panel.permissions import check_auth
from app.database.models import Code, User
from app.database.db import Session


ENTER_CODE = range(1)


def pass_code(update, context):
    session = Session()
    user_id = update.message.chat_id
    code_value = update.message.text.strip()

    code = session.query(Code).filter(Code.value == code_value).first()
    user = session.query(User).filter(Code.value == code_value).first()

    if code and user:
        session.query(User).filter(user_id == User.tg_chat_id).update({User.score: User.score + code.cost})
        session.commit()

        context.bot.send_message(
            chat_id=user_id,
            text=f"Код верный, вам начислено {code.cost} очков"
        )
    else:
        context.bot.send_message(
            chat_id=user_id,
            text=f"Код не верен или введен некорректно"
        )
    session.close()
    return ConversationHandler.END


def enter_code(update, context):
    if check_auth(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите код'
        )
        return ENTER_CODE
    else:
        return ConversationHandler.END


dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler(command='code', callback=enter_code)],
    states={
        ENTER_CODE: [MessageHandler(filters=Filters.text, callback=pass_code)]
    },
    fallbacks=[]
))