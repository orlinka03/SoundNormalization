from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi_users import FastAPIUsers
import os

from src.config import access_key, secret_key, endpoint_url, bucket_name
from src.user.S3Client import S3Client
from src.user.base_config import current_user
from src.user.models import User

router = APIRouter()

# Инициализируем S3Client с использованием переменных окружения
s3_client = S3Client(
    access_key=access_key,
    secret_key=secret_key,
    endpoint_url=endpoint_url,
    bucket_name=bucket_name,
)

@router.post("/uploadfile")
async def upload_file(file: UploadFile, user: User = Depends(current_user)):
    user_id = str(user.id)  # Получаем ID текущего пользователя
    try:
        await s3_client.create_directory(user_id)
        object_name = f"{user_id}/{file.filename}"
        await s3_client.upload_file(file, object_name)
        return {"message": f"Файл '{file.filename}' успешно загружен в Selectel S3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

@router.delete("/files/delete/{filename}")
async def delete_file(filename: str, user: User = Depends(current_user)):
    try:
        await s3_client.delete_file(user_id=str(user.id), filename=filename)
        return {"message": f"Файл '{filename}' успешно удалён из директории пользователя."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {str(e)}")

@router.get("/files")
async def get_user_files(user: User = Depends(current_user)):
    try:
        files = await s3_client.list_files(user_id=str(user.id))
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка файлов: {str(e)}")
