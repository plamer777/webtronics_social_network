"""This file contains a services for 'post' table of the database"""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.base_service import BaseService
from dao.models import User
from dao.post_dao import PostDAO
from services.schemas import PostSchema
# ---------------------------------------------------------------------------


class PostService(BaseService[PostDAO, PostSchema]):
    """This class provides a business logic to create, get, update,
    and delete posts"""
    def __init__(
            self, dao: PostDAO = PostDAO(),
            schema: type[PostSchema] = PostSchema) -> None:
        """Initialize the PostService"""
        super().__init__(dao, schema)

    async def update_favorites(
            self, db: AsyncSession, post_id: int, user: User) -> None:
        """This method serves to update the favorites field of a post model
        :param db: the database connection object
        :param post_id: the id of the post to update
        :param user: the user model to add or remove to/from the favorites
        field
        """
        post = await self._dao.get_by_id(db, post_id)
        if user.id == post.owner_id:
            raise HTTPException(
                400, 'You cannot like or dislike your own post')

        if user not in post.favorites:
            post.favorites.append(user)
        else:
            post.favorites.remove(user)
        await self._dao.partial_update(db, post)

    async def get_by_owner(
            self, db: AsyncSession, user: User) -> list[PostSchema]:
        """This method serves to retrieve a post by its owner id
        :param db: the database connection object
        :param user: the user model with id to retrieve the post by
        :return: a list of PostSchema instances
        """
        posts = await self._dao.get_by_owner_id(db, user.id)
        return [self._schema.from_orm(post) for post in posts]

