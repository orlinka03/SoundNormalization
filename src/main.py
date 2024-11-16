from fastapi import FastAPI, Depends
from fastapi_users import fastapi_users, FastAPIUsers

from src.user.base_config import auth_backend, current_user
from src.user.manager import get_user_manager
from src.user.models import User
from src.user.schemas import UserRead, UserCreate
from src.file.router import router as file_router  # Импортируйте ваш роутер для работы с файлами

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(
    title="Sound Normalization"
)

# Аутентификация
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Регистрация
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Роуты для работы с файлами
app.include_router(
    file_router,  # Добавляем роутер для работы с файлами
    prefix="/files",  # Префикс для роутов
    tags=["files"],  # Тэг для маршрутов
)

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.name}"
