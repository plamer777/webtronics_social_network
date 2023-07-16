"""This file contains a PostDAO class to get access to the posts table in the
database"""
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dao.base_dao import BaseDAO
from dao.models import Post
# --------------------------------------------------------------------------


class PostDAO(BaseDAO[Post]):
    """The PostDAO class provides access to the posts table in the database"""
    def __init__(self, model: Post = Post) -> None:
        super().__init__(model)

    async def partial_update(self, db: AsyncSession, post: Post) -> None:
        db.add(post)
        await db.commit()
        await db.close()

    async def get_by_owner_id(
            self, db: AsyncSession, user_id: int) -> Sequence[Post]:
        post = await db.execute(
            select(self._model).where(self._model.owner_id == user_id))
        await db.close()
        return post.scalars().unique().all()
