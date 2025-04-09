from datetime import datetime

from sqlalchemy import MetaData, Table, Column, String, Integer, TIMESTAMP, ForeignKey, Boolean

metadata = MetaData()

status = Table(
    "status",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False)
)

parameters = Table(
    "parameters",
    metadata,
    Column("id", Integer, primary_key=True),
)

file = Table(
    "file",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("path", String, nullable=False),
    Column("status_id", Integer, ForeignKey(status.c.id)),
    Column("version", String),
    Column("parameters_id", Integer, ForeignKey(parameters.c.id)),
)
