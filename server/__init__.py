import os
from dotenv import load_dotenv


load_dotenv(dotenv_path='../')

from .application import create_app
app = create_app(
    DATABASE_PORT = os.getenv('DATABASE_PORT'),
    DATABASE_HOST = os.getenv('DATABASE_HOST'),
    DATABASE_USER = os.getenv('DATABASE_USER'),
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD'),
    STATIC_FOLDER = os.getenv('STATIC_FOLDER'),
    TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER'),
    SECRET_KEY = os.getenv('SECRET_KEY')
    )

from .routes import *
