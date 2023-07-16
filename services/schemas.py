"""This file contains Pydantic schemas to serialize and validate data"""
from datetime import datetime
from email_validate import validate
from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator
from utils import validate_passwords, encode_password
# ------------------------------------------------------------------------


class BaseUserSchema(BaseModel):
    """This class is a base schema for all user schemas"""
    email: EmailStr
    username: str
    name: str | None = None
    surname: str | None = None
    age: PositiveInt | None = None
    avatar: str | None = None

    @validator('age')
    def validate_age(cls, value: PositiveInt) -> PositiveInt:
        """This method serves to validate the age of a user"""
        if value is not None:
            if value < 14:
                raise ValueError('The minimum age to register is 14 years')
            elif value > 100:
                raise ValueError('The maximum age to register is 100 years')

        return value

    class Config:
        orm_mode = True


class BasePostSchema(BaseModel):
    """This class is a base schema for all post schemas"""
    text: str
    image: str | None = None
    favorites: list[int] = []

    class Config:
        orm_mode = True


class PostSchema(BasePostSchema):
    """This class represents a post schema for GET requests and responses"""
    id: int
    owner_id: int | None

    @root_validator(pre=True)
    def validate_favorites(cls, values: dict) -> dict:
        """This method serves to change the list of favorites"""
        values = dict(values)
        favorites = values.get('favorites', [])
        if favorites  and type(favorites[0]) is not int:
            values['favorites'] = [item.id for item in favorites]

        return values


class UserRegisterSchema(BaseUserSchema):
    """This class represents a user registration schema"""
    password: str
    password_repeat: str

    @root_validator
    def validate_password(cls, values: dict) -> dict:
        """This method serves to validate the passwords during registration
        process"""
        values = dict(values)
        password = values.get('password')
        password_repeat = values.pop('password_repeat', None)
        if validate_passwords(password, password_repeat):
            values['password'] = encode_password(password)
            return values

    @validator('email')
    def validate_email(cls, value: EmailStr) -> EmailStr:
        if not validate(value, check_blacklist=False, check_smtp=True):
            raise ValueError(
                'It looks like provided email address does not exist')
        return value


class UserSchema(BaseUserSchema):
    """This class represents a user schema for GET requests and responses"""
    id: int
    liked_posts: list[int] = []
    created_posts: list[int] = []

    @root_validator(pre=True)
    def refactor_data(cls, values: dict) -> dict:
        """This method serves to refactor the liked_posts and created_posts
        fields"""
        values = dict(values)

        liked_posts = values.get('liked_posts', [])
        if liked_posts and type(liked_posts[0]) is not int:

            values['liked_posts'] = [item.id for item in liked_posts]

        created_posts = values.get('created_posts', [])

        if created_posts and type(created_posts[0]) is not int:
            values['created_posts'] = [item.id for item in created_posts]

        return values


class UserLoginSchema(BaseUserSchema):
    """This class serves as serializer during authentication process"""
    password: str
    username: str | None = None


class UserUpdateSchema(BaseUserSchema):
    """This class serves as a schema to update user data"""
    id: int | None = None
    email: EmailStr | None = None
    username: str | None = None

    @root_validator(pre=True)
    def exclude_fields(cls, values: dict) -> dict:
        """This method serves to exclude fields that should not be changed"""
        values = dict(values)
        values.pop('email', None)
        values.pop('id', None)
        values.pop('username', None)
        return values


class CreatePostSchema(BasePostSchema):
    """This class serves as a schema to create a new post"""
    owner_id: int | None = None

    @root_validator(pre=True)
    def exclude_fields(cls, values: dict) -> dict:
        """This method serves to exclude fields that should not be set by the
        user"""
        values = dict(values)
        values.pop('favorites', None)
        return values


class UpdatePostSchema(BasePostSchema):
    """This class serves as a schema to update a post data"""
    id: int | None = None
    favorites: None = None
    updated_at: datetime = datetime.now()


class Token(BaseModel):
    """This class serves as a schema for access and refresh tokens"""
    access: str
    refresh: str
