import pymongo
import os
from pathlib import Path
import environ
from aioredis import Redis
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
HOST = env('HOST')

# Database MongoDB
MONGO_CLIENT = pymongo.MongoClient(env('MONGO_CLIENT'))
try:
    MONGO_CLIENT.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
MONGO_DB = MONGO_CLIENT[os.environ.get('MONGO_DB')]
USERS = MONGO_DB[os.environ.get('MONGO_COLLECTION')]
REDIS_STORAGE = Redis(host='redis', decode_responses=True)
