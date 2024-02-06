import os
from decouple import config
from datetime import timedelta
import re

BASE_DIR = os.path.dirname(os.path.realpath(__file__)) # Configuring the path the Base Directory

#We want to use regular expresion to to tweek the uri to accept postgresql by replacing the postgres:// route with postgresql://

uri = os.getenv('DATABASE_URL')
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
    
class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret') # decouple imports the config file and searches for the .env file then, gets whatever secret key you have in there
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=120)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=120)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')

class DevConfig(Config):
    # DEBUG = config('DEBUG', cast=bool) # cast=bool just tells that line of code that it is expecting a boolean value
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Not to track changes
    SQLALCHEMY_ECHO = True # To show our database when it creates. This just gives us a visible equivalence of what our database looks like when we create it.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(BASE_DIR, 'db.sqlite3') # Note, db.sqlite3 this is the databse we're using. Here, 

class TestConfig(Config): # This is for testing. Note by putting config in the bracket, the TestConfig assumes the values of the Config, so no need typing them out.
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://' # We will be using a memory database. Unlike what we have above, the sqlite has three slashes (sqlite:///') which simply says it's using an actual database but the slashes or forward thick is two (sqlite://') it means it's using a memory database. Note that a memory database uses the computer's memory and not storage so, it could be wiped off when the computer goes off. 
    
class ProdConfig(Config): # This is for production. Note how the ProdCOnfig class is inheriting from the config class ProdConfig(Config)
    SQLALCHEMY_DATABASE_URI = uri # Since we have defined the URI above, we just need to assign it here.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config('DEBUG', False, cast=bool) # You have to set debug to False in Production so that when you encounter an error, it won't display on your UI screen because that's quite messy most times. Those error messages we get on insomnia is as a result of debug=True
    # Now head to the runserver file and configure that too since we'll be running the file when we want to start the application

# The config will be used to import settings/classes in our __init__.py file so technically, the 'dev', 'prod', and 'test' points to the classes 'DevConfig', 'ProdConfig', and 'ProdConfig' Respectively so it will be easy to import them.
config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}