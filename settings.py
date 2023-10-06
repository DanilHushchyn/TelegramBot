import pymongo
from aioredis import Redis
import os
from datetime import timedelta
from pathlib import Path
import environ
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

BASE_DIR = Path(__file__).resolve().parent

# django-environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))




# BOT
BOT_TOKEN = env('BOT_TOKEN')


# Database MongoDB
MONGO_CLIENT = pymongo.MongoClient(env('MONGO_CLIENT'))
MONGO_DB = MONGO_CLIENT[os.environ.get('MONGO_DB')]
USERS = MONGO_DB[os.environ.get('MONGO_COLLECTION')]
USERS.create_index('user_tg_id', unique=True)
USERS.create_index('user_api_id', unique=True)
USERS.create_index('email', unique=True)
