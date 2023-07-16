"""This file contains base implementation of services to be inherited by
other services"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from dao.base_dao import BaseDAO
# ---------------------------------------------------------------------------
T = TypeVar('T', bound=BaseDAO)
S = TypeVar('S', bound=BaseModel)
# ---------------------------------------------------------------------------


class AbstractService(ABC):
    """This abstract class provides a base requirements for service
    implementation"""
    @abstractmethod
    def __init__(self, dao: BaseDAO) -> None:
        """Initialize the AbstractDAO class"""
        pass

    @abstractmethod
    async def add_new(self, db: AsyncSession, data: BaseModel):
        """This method adds a new item to the database"""
        pass

    @abstractmethod
    async def get_all(self, db: AsyncSession):
        """This method returns all items found in the database"""
        pass

    @abstractmethod
    async def get_by_id(self, db: AsyncSession, uid: int):
        """This method returns a single item from the database found by the
        given uid"""
        pass

    @abstractmethod
    async def update(self, db: AsyncSession, data: BaseModel):
        """This method updates an existing item in the database"""
        pass

    @abstractmethod
    async def delete(self, db: AsyncSession, uid: int):
        """This method deletes an existing item from the database"""
        pass


class BaseService(AbstractService, Generic[T, S]):
    """The BaseDAO class provides a base CRUD logic for all DAO
    implementations"""
    def __init__(self, dao: T, schema: type[S]) -> None:
        """Initialize the BaseDAO class
        :param dao: a DAO class to get access to the database
        """
        self._dao = dao
        self._schema = schema

    async def add_new(self, db: AsyncSession, data: S) -> S:
        """This method adds a new item to the database
        :param db: a database session
        :param data: an instance of a BaseModel with the data to be added
        :return: the newly created item
        """
        try:
            model = await self._dao.add_new(db, data.dict())
            new_model = await self._dao.get_by_id(db, model.id)
            created = self._schema.from_orm(new_model)

        except Exception as e:
            raise HTTPException(
                400, f'There was an error adding the item: {e}')

        return created

    async def get_all(self, db: AsyncSession) -> list[S]:
        """This method returns all models found in the certain table
        :param db: a database session
        :return: a list of BaseModel instances
        """
        all_models = await self._dao.get_all(db)
        schemas = [self._schema.from_orm(model) for model in all_models]

        return schemas

    async def get_by_id(self, db: AsyncSession, uid: int) -> S:
        """This method returns a single model found in the table by the
        provided uid
        :param db: a database session
        :param uid: the id of the model
        :return: the model found in the table or None otherwise
        """
        model = await self._dao.get_by_id(db, uid)
        if model:
            return self._schema.from_orm(model)
        raise HTTPException(
            status_code=404, detail='The requested model is not found')

    async def update(self, db: AsyncSession, data: S) -> None:
        """This method updates an existing model in the table
        :param db: a database session
        :param data: a dictionary containing the data to update
        :return: the updated model or None otherwise
        """
        try:
            await self._dao.update(db, data.dict(exclude_none=True))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f'An error occurred while updating the model: {e}')

    async def delete(self, db: AsyncSession, uid: int) -> None:
        """This method deletes an existing model from the table
        :param db: a database session
        :param uid: the id of the model to delete
        """
        deleted = await self._dao.get_by_id(db, uid)
        if deleted:
            await self._dao.delete(db, deleted)
        else:
            raise HTTPException(
                status_code=404, detail='The requested model does not exist')
