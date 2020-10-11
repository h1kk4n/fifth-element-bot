from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(basedir, ".env")
if os.path.exists(env_path):
    load_dotenv(verbose=True, dotenv_path=env_path)


class Config:
    BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
    TG_OWNER_ID = int(os.environ.get('TG_OWNER_ID', None))
    SHISHI_ID = int(os.environ.get('SHISHI_ID', None))

    DATABASE_URL = os.environ.get('DATABASE_URL', None).replace('postgres', 'postgres+psycopg2')

    APP_URL = os.environ.get('APP_URL', None)
    PORT = int(os.environ.get('PORT', 5000))