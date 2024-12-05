from dataclasses import dataclass

from sqlalchemy import TIMESTAMP


@dataclass
class File:
    name: str
    path: str
    status_id: int
    version: str
    id:int=int()

@dataclass
class Role:
    name: str
    permissions: str
    id: int=int()

@dataclass
class Status:
    name: str
    id: int=int()

@dataclass
class User:
    name: str
    email: str
    hashed_password: str
    role_id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    id: int=int()