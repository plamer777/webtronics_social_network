"""This file contains a UserService class with necessary business logic"""
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import DecodeError
from sqlalchemy.ext.asyncio import AsyncSession
from services.base_service import BaseService
from dao.models import User
from dao.user_dao import UserDAO
from services.schemas import UserSchema, UserLoginSchema, Token, \
    UserRegisterSchema
from utils import decode_token, check_password, create_token, get_db
# ---------------------------------------------------------------------------
oauth_schema = HTTPBearer(auto_error=False)
# ---------------------------------------------------------------------------


class UserService(BaseService[UserDAO, UserSchema]):
    """The UserService class provides all necessary methods to get and check
    user data received from DAO"""
    def __init__(
            self, dao: UserDAO = UserDAO(),
            schema: type[UserSchema] = UserSchema, token: type[Token] = Token
    ) -> None:
        """Initialize the UserService class
        :param dao: UserDAO instance to get and save user data
        :param schema: UserSchema class to represent user data
        :param token: Token class having access and refresh tokens
        """
        super().__init__(dao, schema)
        self._token = token

    async def add_new(
            self, db: AsyncSession, data: UserRegisterSchema) -> UserSchema:
        """This method adds a new user to the database if the user is not
        already exists
        :param db: database connection object
        :param data: UserRegisterSchema instance representing the user data
        :return: UserSchema instance representing the full user data
        """
        found_user = await self._dao.get_by_email(db, data.email)
        if found_user:
            raise HTTPException(
                400, f'User with email {data.email} already exists')

        found_user = await self._dao.get_by_username(db, data.username)
        if found_user:
            raise HTTPException(
                400, f'User with username {data.username} already exists')

        return await super().add_new(db, data)

    async def get_by_email(self, db: AsyncSession, email: str) -> UserSchema:
        """This method serves to get user by email
        :param db: database connection object
        :param email: email of the user to retrieve
        :return: UserSchema instance representing the full user data
        """
        found = await self._dao.get_by_email(db, email)
        if not found:
            raise HTTPException(
                status_code=404, detail=f'User with email {email} not found')
        return self._schema.from_orm(found)

    async def authenticate_and_authorize(
            self, db: AsyncSession, user_data: UserLoginSchema | None,
            refresh_token: str = '') -> Token:
        """This method serves to authenticate and authorize user by email and
        password or refresh token. Use either user_data or refresh_token
        parameter, not both at once
        :param db: database connection object
        :param user_data: UserLoginSchema instance containing email and
        password of the current user
        :param refresh_token: a string representing a refresh token
        process requires email and password or refresh token
        :return: Token instance containing access and refresh tokens
        """
        if refresh_token:
            try:
                data = decode_token(refresh_token)
                user_data = UserLoginSchema(
                    email=data.get('email'), password='')
            except DecodeError as e:
                raise HTTPException(
                    400, f'Cannot decode provided token, an error: {e}')
        found_user = await self._dao.get_by_email(db, user_data.email)
        if not found_user:
            raise HTTPException(
                404, f'User with email {user_data.email} is not found')

        elif not refresh_token and not check_password(
                user_data.password, found_user.password):
            raise HTTPException(
                400, 'Email or password is incorrect')

        token_pair = create_token({'email': found_user.email})
        tokens = Token(**token_pair)

        return tokens

    async def get_current(
            self, db: Annotated[AsyncSession, Depends(get_db)],
            credentials: HTTPAuthorizationCredentials = Depends(oauth_schema)
    ) -> User:
        """This method serves to get the current user by provided token. Db
        and token instance will be got automatically
        :param db: database connection object
        :param credentials: an HTTPAuthorizationCredentials object containing
        the token
        :return: a User instance
        """
        try:
            token = credentials.credentials
            data = decode_token(token)
        except Exception as e:
            raise HTTPException(401, f'Cannot decode token, an error: {e}')
        email = data.get('email')
        user = await self._dao.get_by_email(db, email)
        if not user:
            raise HTTPException(404, f'User with email {email} is not found')

        return user
