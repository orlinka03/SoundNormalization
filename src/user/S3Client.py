import logging
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from fastapi import UploadFile

logging.basicConfig(level=logging.INFO)  # Настройка логирования

class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def create_directory(self, user_id: str):
        async with self.get_client() as client:
            # Добавляем ключ с конечной косой чертой, что интерпретируется как "папка"
            key = f"{user_id}/"
            try:
                response = await client.put_object(Bucket=self.bucket_name, Key=key, Body=b"")
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    logging.info(f"Директория для пользователя '{user_id}' создана успешно.")
                else:
                    logging.error(f"Не удалось создать директорию. Код ответа: {response['ResponseMetadata']['HTTPStatusCode']}")
            except Exception as e:
                logging.error(f"Ошибка при создании директории: {e}")

    async def upload_file(self, file: UploadFile, object_name: str):
        async with self.get_client() as client:
            file_content = await file.read()  # Чтение содержимого файла
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_content
            )

    async def delete_file(self, user_id: str, filename: str):
        """Удаляет файл из S3 в директории пользователя."""
        key = f"{user_id}/{filename}"  # Формируем путь к файлу на основе user_id и имени файла
        async with self.get_client() as client:
            try:
                response = await client.delete_object(Bucket=self.bucket_name, Key=key)
                if response['ResponseMetadata']['HTTPStatusCode'] == 204:
                    logging.info(f"Файл '{filename}' пользователя '{user_id}' успешно удалён.")
                else:
                    logging.error(
                        f"Не удалось удалить файл '{filename}'. Код ответа: {response['ResponseMetadata']['HTTPStatusCode']}")
            except Exception as e:
                logging.error(f"Ошибка при удалении файла: {e}")
                raise e  # Для правильного перехвата и обработки исключения в маршруте

    async def list_files(self, user_id: str):
        prefix = f"{user_id}/"
        async with self.get_client() as client:
            try:
                response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
                files = [
                    obj["Key"].replace(prefix, "") for obj in response.get("Contents", [])
                ]
                logging.info(f"Файлы пользователя '{user_id}' успешно получены.")
                return files
            except Exception as e:
                logging.error(f"Ошибка при получении списка файлов: {e}")
                raise