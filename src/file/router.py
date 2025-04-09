import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi_users import FastAPIUsers
import os

from src.config import access_key, secret_key, endpoint_url, bucket_name
from src.dbmodels import File, Status
from src.user.S3Client import S3Client
from src.user.base_config import current_user
from src.user.models import User
from util.repositories.db_repos import SQLAlchemyPostgresqlDataclassRepository

router = APIRouter()

logging.basicConfig(level=logging.INFO)

# Инициализируем S3Client с использованием переменных окружения
s3_client = S3Client(
    access_key=access_key,
    secret_key=secret_key,
    endpoint_url=endpoint_url,
    bucket_name=bucket_name,
)

file_repo = SQLAlchemyPostgresqlDataclassRepository(File)
status_repo = SQLAlchemyPostgresqlDataclassRepository(Status)


@router.post("/uploadfile")
async def upload_file(file: UploadFile, path: str, status: int , user: User = Depends(current_user)):
    logging.info(f"Received status: {status}")
    user_id = str(user.id)  # Получаем ID текущего пользователя
    try:
        await s3_client.create_directory(user_id)
        object_name = f"{user_id}/{file.filename}"
        file_cr = File(file.filename, status, 'v1.0', path)
        logging.info(f"File object created with status: {status}")
        file_repo.add(file_cr)
        await s3_client.upload_file(file, object_name)
        logging.info(f"File {file.filename} uploaded to S3")
        return {"message": f"Файл '{file.filename}' успешно загружен в Selectel S3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

@router.delete("/files/{filename}")
async def delete_file(filename: str, user: User = Depends(current_user)):
    try:
        await s3_client.delete_file(user_id=str(user.id), filename=filename)
        file_repo.remove_by_name(filename)
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


@router.get("/files/{filename}")
async def get_file_by_name(filename: str, user: User = Depends(current_user)):
    try:
        # Retrieve the file from S3
        file_content = await s3_client.get_file_by_name(user_id=str(user.id), filename=filename)

        if file_content is None:
            raise HTTPException(status_code=404, detail="Файл не найден.")

        # Optionally return the file content (e.g., as base64, or save to disk)
        return {"filename": filename,
                "content": file_content}  # Adjust according to how you want to return the file content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения файла: {str(e)}")
