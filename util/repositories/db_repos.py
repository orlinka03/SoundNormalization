import copy
from abc import ABC
from dataclasses import asdict

from dotenv import dotenv_values
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, select, update, delete, ForeignKey
from sqlalchemy.dialects.postgresql import insert

from util.repositories.base_repo import BaseRepository


class SQLAlchemyPostgresqlDataclassRepository(BaseRepository, ABC):
    """
    Based on  https://docs.sqlalchemy.org/en/20/tutorial/data_select.html
    """
    DATABASE_ACCESS_URI = dotenv_values(".env").get("DATABASE_ACCESS_URI")
    type_mapping = {
        "str": Text,
        "int": Integer,
    }

    primary_field_name = "id"

    def __init__(self, reference_type):
        super().__init__(reference_type)

        self.engine = create_engine(f"postgresql+psycopg2://" + self.DATABASE_ACCESS_URI)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def _get_table_name(self):
        return self._reference_type.__name__.lower()

    def create_model(self) -> Table:
        model_fields_data = copy.deepcopy(self._reference_type.__annotations__)
        del model_fields_data[self.primary_field_name]

        columns = [Column(self.primary_field_name, Integer, primary_key=True, autoincrement=True)]

        for field_name, field_type in zip(model_fields_data.keys(), model_fields_data.values()):
            column_type = self.type_mapping[field_type.__name__]
            column_obj = column_type()

            if field_name[-len(self.primary_field_name):] == self.primary_field_name:
                foreign_key_name = field_name[
                                   :-len(self.primary_field_name) - 1].lower() + f".{self.primary_field_name}"
                column_obj = ForeignKey(foreign_key_name)

            columns.append(
                Column(field_name, column_obj)
            )

        table = Table(
            self._get_table_name(),
            self.metadata,
            *columns
        )

        self.metadata.create_all(self.engine)

        return table

    def add(self, obj) -> None:
        with self.engine.connect() as connection:
            table_to_append = self.metadata.tables[self._get_table_name()]
            dictation_of_object = asdict(obj)
            del dictation_of_object[self.primary_field_name]
            connection.execute(insert(table_to_append), [dictation_of_object])
            connection.commit()

    def get(self, reference: int):
        with self.engine.connect() as connection:
            table = self.metadata.tables[self._get_table_name()]
            cursor = connection.execute(select(table).where(getattr(table.c, self.primary_field_name) == reference))
            objects = cursor.mappings().all()

            if objects:
                return self._reference_type(**objects[0])
            else:
                raise Exception(f"Object of {self._reference_type} with {reference=} not found!")

    def update(self, obj):
        with self.engine.connect() as connection:
            table = self.metadata.tables[self._get_table_name()]
            reference = getattr(obj, self.primary_field_name)
            dictation_of_object = asdict(obj)
            del dictation_of_object[self.primary_field_name]

            connection.execute(update(table).where(getattr(table.c, self.primary_field_name) == reference).values(
                **dictation_of_object), [])
            connection.commit()

    def remove(self, reference: int) -> None:
        with self.engine.connect() as connection:
            table = self.metadata.tables[self._get_table_name()]
            connection.execute(delete(table).where(getattr(table.c, self.primary_field_name) == reference))
            connection.commit()

    def list(self):
        with self.engine.connect() as connection:
            table = self.metadata.tables[self._get_table_name()]
            cursor = connection.execute(select(table))
            return [self._reference_type(**item) for item in cursor.mappings().all()]
