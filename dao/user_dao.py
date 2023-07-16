"""This file contains a UserDAO class to get access to the users table in the
database"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dao.base_dao import BaseDAO
from dao.models import User
# ---------------------------------------------------------------------------


class UserDAO(BaseDAO[User]):
    """The UserDAO class provides access to the users table in the database"""
    def __init__(self, model: User = User) -> None:
        super().__init__(model)

    async def get_by_email(self, db: AsyncSession, email: str) -> User:
        found_user = await db.execute(
            select(self._model).where(self._model.email == email))
        await db.close()
        return found_user.scalar()

    async def get_by_username(self, db: AsyncSession, username: str) -> User:
        """This method returns a user found by his username
        :param db: the database connection object
        :param username: the username of the user to find
        :return: the User instance
        """
        found_user = await db.execute(
            select(self._model).where(self._model.username == username))
        await db.close()
        return found_user.scalar()
