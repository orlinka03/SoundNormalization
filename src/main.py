import tempfile
from typing import Annotated

from fastapi import FastAPI, Depends, UploadFile, Form
from starlette.responses import FileResponse

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from src.file.sound_func import get_file_extension, apply_compression, load_audio, get_file_type, save_or_replace_audio, \
    FileType
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

@app.post("/file/compress")
def compress_file(file: UploadFile,
                  thresh: Annotated[int, Form()],
                  ratio: Annotated[float, Form()]
                  ):
    try:
        print("Hello world")
        print(thresh, ratio)
        print(file.filename)
        # Добавить проверку на тип файла
        # Отправка параметров компрессии thresh, ratio
        # Тоже самое для обрезания

        file_path = "uploaded.mp4"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"{get_file_extension(file_path)}")
        temp_file.close()
        result = apply_compression(load_audio(file_path, get_file_type(file_path)), thresh, ratio)
        save_or_replace_audio(
            file_path,
            result,
            get_file_type(file_path),
            temp_file.name
        )
        return FileResponse(temp_file.name)
    except:
        return {"message": "Error!"}