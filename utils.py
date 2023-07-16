"""This file contains utility functions"""
import os
import re
from base64 import b64encode
from calendar import timegm
from datetime import datetime, timedelta
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from uuid import uuid4
import jwt
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from dao import LocalSession
from settings import JWT_SECRET, JWT_ALGO, HASH_ALGO, HASH_SALT, HASH_ITERS, \
    REFRESH_TOKEN_EXP, ACCESS_TOKEN_EXP
# ---------------------------------------------------------------------------


async def get_db() -> AsyncSession:
    """The function serves to return an async database session
    :return: an AsyncSession instance
    """
    async with LocalSession() as db_session:
        return db_session


def validate_passwords(password: str, password_confirm: str) -> bool:
    """This function validates a pair of given passwords
    :param password: a string representing the password
    :param password_confirm: a string representing the password confirmation
    :return: True if the password is valid and false otherwise
    """
    if not password or password != password_confirm:
        raise ValueError('The password and password_repeat are required '
                         'and must be the same')
    elif len(password) < 8:
        raise ValueError("Password length must be at least 8 characters")
    elif len(password) > 50:
        raise ValueError("Password length must be less than 50 characters")
    elif not re.match(r'(?=.*[A-Z].*[A-Z].*[A-Z])(?=.*[0-9]).+', password):
        raise ValueError("Password must contain at least one digit and 3 "
                         "upper-case letters")

    return True


def create_token(data: dict) -> dict[str, str]:
    """This function creates an access token and a refresh token for the
    given data
    :param data: a dict containing the data
    :return: a dict containing the access token and the refresh token
    """
    data['exp'] = timegm(
        (datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXP)).timetuple())
    access_token = jwt.encode(data, key=JWT_SECRET, algorithm=JWT_ALGO)
    data['exp'] = timegm(
        (datetime.now() + timedelta(days=REFRESH_TOKEN_EXP)).timetuple())
    refresh_token = jwt.encode(data, key=JWT_SECRET, algorithm=JWT_ALGO)

    return {'access': access_token, 'refresh': refresh_token}


def decode_token(token: str) -> dict:
    """This function serves to decode provided token
    :param token: a string representing the token to decode
    :return: a dict containing the data extracted from the token
    """
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    return data


def encode_password(password: str) -> str:
    """This function serves to encode provided password
    :param password: a string representing the password
    :return: a string representing the encoded password
    """
    encoded_password = pbkdf2_hmac(
        HASH_ALGO, password.encode('utf-8'), HASH_SALT, HASH_ITERS)
    return b64encode(encoded_password).decode('utf-8')


def check_password(password: str, validated_password: str) -> bool:
    """This function serves to validate the provided password
    :param validated_password: a string representing the validated password
    :param password: a string representing the password to validate
    :return: True if the password is valid and False otherwise
    """
    hashed_password = encode_password(password)
    return compare_digest(hashed_password, validated_password)


def save_to_file(filename: str, data: bytes) -> None:
    """This function serves to save the provided data to a file
    :param filename: a string representing the filename to save
    :param data: a bytes object representing the data to save
    """
    try:
        with open(filename, 'wb') as fout:
            fout.write(data)

    except Exception as e:
        print(f'Failed to write data to file {filename}, error: {e}')


def create_safe_filename(filename: str) -> tuple[bool, str]:
    """This function serves to create a safe filename from the provided
    filename
    :param filename: a string representing the initial filename
    :return: a tuple containing the boolean indicating whether the filename
    was created successfully and the resulting filename or exception message
    """
    try:
        extension = filename.split('.')[-1]
        safe_filename = uuid4().hex + f'.{extension}'
        return True, safe_filename

    except Exception as e:
        return False, f'Failed to create filename {filename}, error: {e}'


def get_filepath(root_dir: str, filename: str) -> str:
    """This function serves to create an independent filepath for any OS
    :param root_dir: the root directory of the files
    :param filename: a string representing the filename
    :return: a string representing the filepath
    """
    return os.path.join(root_dir, filename)


async def save_file_and_get_url(
        root_url: str, root_dir: str, file_obj: UploadFile) -> str:
    """This function serves to save the provided file creating safe filename
    and return the url of the file
    :param root_url: the root url of the file's storage
    :param root_dir: a file storage directory path
    :param file_obj: an instance of UploadFile
    """
    file_data = await file_obj.read()
    is_success, result = create_safe_filename(file_obj.filename)
    if not is_success:
        raise HTTPException(400, result)
    save_to_file(get_filepath(root_dir, result), file_data)
    return root_url + result


def create_path(path: str) -> None:
    """This function serves to create a path if it does not exist
    :param path: a string representing the path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def read_from_file(filename: str) -> str:
    """This function serves to read data from text files
    :param filename: a string representing a name of file with path to read
    :return: a text data
    """
    try:
        with open(filename, encoding='utf-8') as fin:
            return fin.read()
    except Exception as e:
        print(f'There was an error during reading a file: {e}')
        return ''
