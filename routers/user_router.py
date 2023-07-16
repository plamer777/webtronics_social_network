"""This file contains router for 'users' route"""
from fastapi import Depends, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from container import user_service
from services.schemas import (UserRegisterSchema, UserSchema, UserLoginSchema,
    Token, UserUpdateSchema)
from settings import AVA_URL, AVA_ROOT
from utils import get_db, get_filepath, save_file_and_get_url
# --------------------------------------------------------------------------
user_router = APIRouter(tags=['users'])
# --------------------------------------------------------------------------


@user_router.post(
    '/users/register/', summary='Register a new user',
    description='This route allows to add new user to the database')
async def register_user(
        username=Form(), email=Form(), name=Form(default=None),
        surname=Form(default=None), age=Form(default=None),
        password=Form(), password_repeat=Form(),
        avatar: UploadFile = None,
        db: AsyncSession = Depends(get_db)) -> UserSchema:
    """This view serves to add a new user to the database
    :param name: a string representing the name of the user
    :param username: a string representing the username
    :param email: a string representing user email
    :param surname: a string representing the surname of the user
    :param age: an integer representing user age
    :param password: a string representing user password
    :param password_repeat: a string representing password confirmation
    :param avatar: an UploadFile object containing image representing user
    :param db: a database connection object
    :return: a UserSchema instance
    """
    try:
        user_data = UserRegisterSchema(
            username=username, email=email, name=name, surname=surname,
            age=age, password=password, password_repeat=password_repeat
        )
    except ValidationError as e:
        raise HTTPException(400, str(e))

    if avatar:
        user_data.avatar = await save_file_and_get_url(
            AVA_URL, AVA_ROOT, avatar)
    new_user = await user_service.add_new(db, user_data)
    return new_user


@user_router.post(
    '/users/login/', response_model=Token,
    summary='Authenticate and authorize the user by email and password',
    description='This route allows to log in user account')
async def user_login(
        email=Form(), password=Form(), db: AsyncSession = Depends(get_db)
) -> Token:
    """This view serves to authenticate the user with his email and password
    :param db: a database connection object
    :param email: a string representing user email
    :param password: a string representing user password to log in
    :return: a Token instance with access and refresh tokens
    """
    user_data = UserLoginSchema(email=email, password=password)
    tokens = await user_service.authenticate_and_authorize(db, user_data)
    return tokens


@user_router.post(
    '/users/token/refresh/', response_model=Token, summary='Update token pair',
    description='This route allows to get a new pair of JWT tokens')
async def update_tokens(
        refresh_token: str = Form(), db: AsyncSession = Depends(get_db)
) -> Token:
    """This view serves to update a token pair by using provided refresh token
    :param db: a database connection object
    :param refresh_token: a string representing a refresh token to extract
    user data from
    :return: a Token instance with access and refresh tokens
    """
    tokens = await user_service.authenticate_and_authorize(
        db, None, refresh_token)
    return tokens


@user_router.get(
    '/users/list/', summary='Get list of all users',
    description='This route allows to get a list of all existing users')
async def user_list(db: AsyncSession = Depends(get_db)) -> list[UserSchema]:
    """This view serves to get a list of all users
    :param db: a database connection object
    :return: a list of UserSchema instances
    """
    all_users = await user_service.get_all(db)
    return all_users


@user_router.get(
    '/users/me/', summary='Get current user data',
    description='This route allows to get data about current user')
async def user_account(
        current_user: UserSchema = Depends(user_service.get_current)
) -> UserSchema:
    """This view serves to get a user instance for the current user
    :param current_user: a UserSchema instance
    :return: a UserSchema instance
    """
    return current_user


@user_router.put(
    '/users/me/update/', status_code=204,
    summary='Update current user account',
    description='This route allows to update current user data such as '
                'avatar, name, surname, age')
async def user_account(
        name=Form(default=None), surname=Form(default=None),
        age=Form(default=None), avatar: UploadFile = None,
        db: AsyncSession = Depends(get_db),
        current_user: UserSchema = Depends(user_service.get_current)
) -> None:
    """This view serves to get a user instance for the current user
    :param current_user: a UserSchema instance
    :param db: a database connection object
    :param name: a string representing the name of the user
    :param surname: a string representing the surname of the user
    :param age: an integer representing user age
    :param avatar: an UploadFile object containing image representing user
    avatar
    """
    try:
        user_data = UserUpdateSchema(name=name, surname=surname, age=age)
    except Exception as e:
        raise HTTPException(400, str(e))

    if avatar:
        user_data.avatar = await save_file_and_get_url(
            AVA_URL, AVA_ROOT, avatar)

    user_data.id = current_user.id
    await user_service.update(db, user_data)


@user_router.get(
    '/users/{user_id}/', summary='Get user data by provided id',
    description='This route allows to get user data by any existing user by '
                'his id')
async def single_user(
        user_id: int, db: AsyncSession = Depends(get_db)) -> UserSchema:
    """This view serves to get a single user instance by the provided id
    :param user_id: an integer representing the user identifier
    :param db: a database connection object
    :return: a UserSchema instance
    """
    return await user_service.get_by_id(db, user_id)


@user_router.delete(
    '/users/me/', status_code=204, summary='Delete current user',
    description='This route allows to delete current authenticated user')
async def delete_user(
        current_user: UserSchema = Depends(user_service.get_current),
        db: AsyncSession = Depends(get_db)) -> None:
    """This view serves to delete current user
    :param current_user: a UserSchema instance
    :param db: a database connection object
    """
    await user_service.delete(db, current_user.id)


@user_router.get(
    AVA_URL + '{filename}', summary='Get user avatar',
    description='This route allows to get an image representing user avatar')
async def get_avatar(filename: str) -> FileResponse:
    """This view serves to get a user avatar
    :param filename: the string representing the filename of the avatar
    :return: a FileResponse object
    """
    file_path = get_filepath(AVA_ROOT, filename)
    return FileResponse(file_path)
