"""This file contains different constants to configure the application"""
import os
from pydantic import BaseSettings
# ---------------------------------------------------------------------------


class EnvSettings(BaseSettings):
    """This class serves to get settings from the environment variables"""
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    JWT_SECRET: str
    JWT_ALGO: str
    ACCESS_TOKEN_EXP_H: int
    REFRESH_TOKEN_EXP_D: int
    HASH_ALGO: str
    HASH_SALT: bytes
    HASH_ITERS: int
    API_TITLE: str = 'Server API'
    API_VERSION: str = '1.0.0'

    class Config:
        env_file = '.env'


env_sets = EnvSettings()


POSTGRES_USER = env_sets.POSTGRES_USER
POSTGRES_PASSWORD = env_sets.POSTGRES_PASSWORD
POSTGRES_HOST = env_sets.POSTGRES_HOST
POSTGRES_PORT = env_sets.POSTGRES_PORT
POSTGRES_DB = env_sets.POSTGRES_DB


DB_URL = (
    f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}'
    f':{POSTGRES_PORT}/{POSTGRES_DB}')


AVA_URL = '/images/avatar/'
PICTURE_URL = '/images/picture/'
AVA_ROOT = os.path.join('images', 'avatar')
PICTURE_ROOT = os.path.join('images', 'picture')

JWT_SECRET = env_sets.JWT_SECRET
JWT_ALGO = env_sets.JWT_ALGO
ACCESS_TOKEN_EXP = env_sets.ACCESS_TOKEN_EXP_H
REFRESH_TOKEN_EXP = env_sets.REFRESH_TOKEN_EXP_D

HASH_ALGO = env_sets.HASH_ALGO
HASH_SALT = env_sets.HASH_SALT
HASH_ITERS = env_sets.HASH_ITERS

API_TITLE = env_sets.API_TITLE
DESCRIPTION_FILE = 'description.txt'
API_VERSION = env_sets.API_VERSION
