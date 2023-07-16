"""This file contains Base implementation of DAO"""
from abc import ABC, abstractmethod
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Generic, TypeVar
from dao import BaseModel
# ---------------------------------------------------------------------------
TD = TypeVar('TD', bound=BaseModel)
# ---------------------------------------------------------------------------


class AbstractDAO(ABC):
    """This abstract class provides a base requirements for DAO
    implementation"""
    @abstractmethod
    def __init__(self, model: BaseModel) -> None:
        """Initialize the AbstractDAO class"""
        pass

    @abstractmethod
    async def add_new(self, db: AsyncSession, data: dict):
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
    async def update(self, db: AsyncSession, data: dict):
        """This method updates an existing item in the database"""
        pass

    @abstractmethod
    async def delete(self, db: AsyncSession, uid: int):
        """This method deletes an existing item from the database"""
        pass


class BaseDAO(AbstractDAO, Generic[TD]):
    """The BaseDAO class provides a base CRUD logic for all DAO
    implementations"""
    def __init__(self, model: type[TD]) -> None:
        """Initialize the BaseDAO class
        :param model: the class representing the database model
        """
        self._model = model

    async def add_new(self, db: AsyncSession, data: dict) -> TD:
        """This method adds a new item to the database
        :param db: a database session
        :param data: a dictionary representing the data to create the item
        :return: the newly created item
        """
        new_model = self._model(**data)
        db.add(new_model)
        await db.commit()
        await db.close()
        return new_model

    async def get_all(self, db: AsyncSession) -> Sequence[TD]:
        """This method returns all models found in the certain table
        :param db: a database session
        :return: a list of all models found in the table
        """
        all_models = await db.execute(select(self._model))
        await db.close()
        return all_models.unique().scalars().all()

    async def get_by_id(self, db: AsyncSession, uid: int) -> TD | None:
        """This method returns a single model found in the table by the
        provided uid
        :param db: a database session
        :param uid: the id of the model
        :return: the model found in the table or None otherwise
        """
        model = await db.execute(
            select(self._model).where(self._model.id == uid))
        await db.close()
        return model.scalar()

    async def update(self, db: AsyncSession, data: dict) -> None:
        """This method updates an existing model in the table
        :param db: a database session
        :param data: a dictionary containing the data to update
        :return: the updated model or None otherwise
        """
        await db.execute(
            update(self._model).where(self._model.id == data.get('id')).
            values(**data))
        await db.commit()
        await db.close()

    async def delete(self, db: AsyncSession, model: TD) -> None:
        """This method deletes an existing model from the table
        :param db: a database session
        :param model: the model to delete
        """
        await db.delete(model)
        await db.commit()
        await db.close()
