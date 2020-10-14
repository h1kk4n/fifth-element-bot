from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Filters

from app.database.db import Session, engine
from app.database.models import Code, Base
from app.admin_panel.permissions import check_permissions
from app import dp


CODE_ADD_VALUE, CODE_ADD_COST, CODE_REMOVE_ID = range(3)


# View codes
def view_codes(update, context):
    if check_permissions(update, context):
        session = Session()

        codes = session.query(Code).all()

        codes_list = '<b><i>Список действительных кодов</i></b>:\n' + '\n'.join(str(code) for code in codes)

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=codes_list
        )
        session.close()


# Delete all codes
def drop_codes(update, context):
    if check_permissions(update, context):
        Base.metadata.tables['codes'].drop(bind=engine)
        Base.metadata.tables['codes'].create(bind=engine)

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Таблица кодов сброшена'
        )


# Add code
def code_add_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите сам код'
        )
        return CODE_ADD_VALUE
    else:
        return ConversationHandler.END


def code_add_value(update, context):
    context.user_data['value'] = update.message.text

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите, сколько пользователь получит за ввод данного кода'
    )
    return CODE_ADD_COST


def code_add_done(update, context):
    session = Session()
    try:
        context.user_data['cost'] = int(update.message.text)
        code_id = 1
        try:
            code_id = session.query(Code).order_by(Code.id.desc()).first().id + 1
        except:
            code_id = session.query(Code).count() + 1
        finally:
            code = Code(
                id=code_id,
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
    except ValueError:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Произошла ошибка, скорее всего введено не число, попробуйте добавить код повторно'
        )
    finally:
        session.close()

        return ConversationHandler.END


# Remove code
def code_remove_start(update, context):
    if check_permissions(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите номер кода из списка кодов'
        )
        return CODE_REMOVE_ID
    else:
        return ConversationHandler.END


def code_remove_id(update, context):
    session = Session()
    try:
        code_id = int(update.message.text)

        code = session.query(Code).order_by(Code.id == code_id).first()

        if code:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Код удален'
            )
            session.delete(code)
            session.commit()
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Такой код не найден'
            )
    except ValueError:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Что-то пошло не так, попробуйте ввести команду повторно'
        )

    finally:
        session.close()
        return ConversationHandler.END


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
dp.add_handler(CommandHandler(command='viewcodes', callback=view_codes))
dp.add_handler(CommandHandler(command='dropcodes', callback=drop_codes))


if __name__ == '__main__':
    pass
