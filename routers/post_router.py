"""This file contains router for 'posts' route"""
from fastapi import Depends, HTTPException, UploadFile, Form
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from container import post_service, user_service
from services.schemas import CreatePostSchema, PostSchema, UpdatePostSchema, \
    UserSchema
from settings import PICTURE_URL, PICTURE_ROOT
from utils import get_db, get_filepath, save_file_and_get_url
# --------------------------------------------------------------------------
post_router = APIRouter(tags=['posts'])
# --------------------------------------------------------------------------


@post_router.post(
    '/posts/create/', summary='Create a new post',
    description='This route allows to create a new post')
async def create_post(
        text=Form(), picture: UploadFile = None,
        current_user: UserSchema = Depends(user_service.get_current),
        db: AsyncSession = Depends(get_db)) -> PostSchema:
    """This view serves to create a new post
    :param picture: an image file representing the post's picture
    :param text: the string representing the post text
    :param current_user: a UserSchema instance
    :param db: a database connection object
    :return: a PostSchema instance
    """
    try:
        post_data = CreatePostSchema(
            text=text, owner_id=current_user.id)
    except ValidationError as e:
        raise HTTPException(400, str(e))

    if picture:
        post_data.image = await save_file_and_get_url(
            PICTURE_URL, PICTURE_ROOT, picture)
    new_post = await post_service.add_new(db, post_data)

    return new_post


@post_router.put(
    '/posts/{post_id}/update/', status_code=204, summary='Update post data',
    description='This route allows you to update post data such as a post '
                'text and a picture')
async def update_post(
        post_id: int, text=Form(default=None), picture: UploadFile = None,
        current_user: UserSchema = Depends(user_service.get_current),
        db: AsyncSession = Depends(get_db)) -> None:
    """This view serves to update a post
    :param post_id: the id of the post to update
    :param text: the string representing the post text
    :param picture: an image file representing the post's picture
    :param current_user: a UserSchema instance
    :param db: a database connection object
    """
    post = await post_service.get_by_id(db, post_id)
    if post.owner_id != current_user.id:
        raise HTTPException(403, f'Only owner can update this post')
    post_data = UpdatePostSchema(
        id=post_id, text=text)
    if picture:
        post_data.image = await save_file_and_get_url(
            PICTURE_URL, PICTURE_ROOT, picture)
    await post_service.update(db, post_data)


@post_router.patch(
    '/posts/{post_id}/like/', status_code=204, summary='Like a post',
    description='This route allows to like any post except owned by you')
async def update_favorites(
        post_id: int, db: AsyncSession = Depends(get_db),
        current_user: UserSchema = Depends(user_service.get_current)) -> None:
    """This view serves to update a post favorites list
    :param post_id: the id of the post to update
    :param current_user: a UserSchema instance
    :param db: a database connection object
    """
    await post_service.update_favorites(
        db, post_id, current_user)


@post_router.get(
    '/posts/list/', summary='Get a list of all existing posts',
    description='This route allows you to get all post created by existing '
                'and deleted users')
async def post_list(db: AsyncSession = Depends(get_db)) -> list[PostSchema]:
    """This view serves to get a list of all posts
    :param db: a database connection object
    :return: a list of PostSchema instances
    """
    all_posts = await post_service.get_all(db)
    return all_posts


@post_router.get(
    '/posts/me/', summary='Get all post created by current user',
    description='This route allows to get a list of posts created by the '
                'current user')
async def current_user_posts(
        current_user: UserSchema = Depends(user_service.get_current),
        db: AsyncSession = Depends(get_db)) -> list[PostSchema]:
    """This view serves to get a list of posta created by the current user
    :param current_user: a UserSchema instance
    :param db: a database connection object
    :return: a list of PostSchema instances
    """
    user_posts = await post_service.get_by_owner(db, current_user)
    return user_posts


@post_router.get(
    '/posts/{post_id}/', summary='Get a single post by its id',
    description='This route allows to get a post data by provided id')
async def single_post(
        post_id: int, db: AsyncSession = Depends(get_db)) -> PostSchema:
    """This view serves to get a single post by its id
    :param post_id: the id of the post to retrieve
    :param db: a database connection object
    :return: a PostSchema instance
    """
    return await post_service.get_by_id(db, post_id)


@post_router.delete(
    '/posts/{post_id}/', status_code=204, summary='Delete post by provided id',
    description='This route allows to delete any post by its id created by '
                'the current user')
async def delete_post(
        post_id: int,
        current_user: UserSchema = Depends(user_service.get_current),
        db: AsyncSession = Depends(get_db)) -> None:
    """This view serves to delete a post by provided id
    :param post_id: an integer representing post id to delete
    :param current_user: a UserSchema instance
    :param db: a database connection object
    """
    deleted_post = await post_service.get_by_id(db, post_id)
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(403, 'You have not credentials to delete the post')
    await post_service.delete(db, post_id)


@post_router.get(
    PICTURE_URL + '{filename}', summary='Get post picture',
    description='This route allows to get a post picture if it exists')
async def get_avatar(filename: str) -> FileResponse:
    """This view serves to get a post picture
    :param filename: the string representing the filename of the picture
    :return: a FileResponse object
    """
    file_path = get_filepath(PICTURE_ROOT, filename)
    return FileResponse(file_path)
