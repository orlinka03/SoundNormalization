import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, exceptions

from src.config import access_key, secret_key, endpoint_url, bucket_name
from src.user.models import User
from src.user.utils import get_user_db
from src.user.S3Client import S3Client  # Импортируем S3Client

SECRET = "SECRET"

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 2

        created_user = await self.user_db.create(user_dict)

        # Создаем экземпляр S3Client и создаем директорию для пользователя
        s3_client = S3Client(
            access_key=access_key,
            secret_key=secret_key,
            endpoint_url=endpoint_url,
            bucket_name=bucket_name,
        )

        try:
            await s3_client.create_directory(str(created_user.id))
        except Exception as e:
            print(f"Ошибка при создании директории: {str(e)}")

        await self.on_after_register(created_user, request)
        return created_user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: models.UP, token: str, request: Optional[Request] = None
    ) -> None:
        return  # pragma: no cover

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
