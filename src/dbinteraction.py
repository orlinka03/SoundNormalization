from src.dbmodels import File, Status, CustomUser
from util.repositories.db_repos import SQLAlchemyPostgresqlDataclassRepository

user = SQLAlchemyPostgresqlDataclassRepository(CustomUser)
file_repo = SQLAlchemyPostgresqlDataclassRepository(File)
status_repo = SQLAlchemyPostgresqlDataclassRepository(Status)

file = File("name", 1, "v1.0", 'path')
file_repo.add(file)

print(file_repo.list_name())
