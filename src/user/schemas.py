import uuid
from typing import Optional

from fastapi_users import schemas
from fastapi_users.schemas import PYDANTIC_V2
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    role_id: int
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    name: str
    email: str
    password: str
    role_id: Optional[int] = 2
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None