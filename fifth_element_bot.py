from app import updater
from config import Config

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater.bot.send_message(
        chat_id=Config.TG_OWNER_ID,
        text='Welcome'
    )

    if Config.APP_URL:
        updater.start_webhook(
            listen='0.0.0.0',
            port=Config.PORT,
            url_path=Config.BOT_TOKEN
        )
        updater.setWebhook(Config.APP_URL+Config.BOT_TOKEN)

    else:
        updater.start_polling()

    updater.idle()
