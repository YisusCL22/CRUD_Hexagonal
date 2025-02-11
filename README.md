<<<markdown
# My CRUD Module Template with Hexagonal Architecture and TDD

This repository provides a generic CRUD module built in Python using **Hexagonal Architecture** and **Test-Driven Development (TDD)**. It is designed as a modular template that can be adapted to multiple web frameworks and technologies. The business logic is completely decoupled from the infrastructure, allowing you to integrate different databases, APIs, and front-end implementations effortlessly.

---

## 📌 Features

✅ **Hexagonal Architecture (Ports & Adapters)**  
✅ **Completely decoupled business logic**  
✅ **Framework-agnostic design** (can work with Django, Flask, FastAPI, etc.)  
✅ **Supports PostgreSQL as a persistence adapter**  
✅ **TDD-based approach with Pytest for high reliability**  
✅ **Easily extendable for new entities and CRUD use cases**  

---

## 📂 Project Structure

The project follows a modular structure:

<<<
my_crud_module/
├── core/                      # Business logic & domain layer
│   ├── __init__.py
│   ├── entities.py            # Entity definitions (e.g., User, Product)
│   ├── interfaces.py          # Repository interface (port)
│   └── use_cases.py           # Business logic (CRUD services)
├── adapters/                  # Infrastructure adapters
│   ├── __init__.py
│   ├── repository_postgresql.py  # PostgreSQL adapter
│   └── api_adapter_example.py     # (Optional) API adapter
├── tests/                     # Unit tests for TDD
│   ├── __init__.py
│   ├── test_use_cases.py
│   └── test_repository_postgresql.py  # (Optional) Integration tests
├── requirements.txt           # Dependencies (e.g., SQLAlchemy, pytest)
└── README.md                  # Documentation file
>>>

---

## 🏗 Domain & Business Logic

### 📌 Entities

Entities are plain data classes that represent core business objects.

<<<python
# core/entities.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Entity:
    id: Optional[int] = None

@dataclass
class User(Entity):
    name: str = ""
    email: str = ""
>>>

### 📌 Repository Interface (Ports)

Defines the CRUD operations that any persistence adapter must implement.

<<<python
# core/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Entity

class Repository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Entity]:
        pass

    @abstractmethod
    def get_all(self) -> List[Entity]:
        pass

    @abstractmethod
    def create(self, entity: Entity) -> Entity:
        pass

    @abstractmethod
    def update(self, id: int, entity: Entity) -> Entity:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
>>>

### 📌 CRUD Service (Use Cases)

Encapsulates business logic, independent of any persistence mechanism.

<<<python
# core/use_cases.py
from typing import List, Optional
from .interfaces import Repository
from .entities import Entity

class CRUDService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def get_entity(self, id: int) -> Optional[Entity]:
        return self.repository.get_by_id(id)

    def list_entities(self) -> List[Entity]:
        return self.repository.get_all()

    def create_entity(self, entity: Entity) -> Entity:
        return self.repository.create(entity)

    def update_entity(self, id: int, entity: Entity) -> Entity:
        return self.repository.update(id, entity)

    def delete_entity(self, id: int) -> bool:
        return self.repository.delete(id)
>>>

---

## 🔌 Adapters

### 📌 PostgreSQL Adapter

Implements the repository interface using SQLAlchemy.

<<<python
# adapters/repository_postgresql.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from core.interfaces import Repository
from core.entities import User

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    def to_entity(self) -> User:
        return User(id=self.id, name=self.name, email=self.email)

    @staticmethod
    def from_entity(user: User) -> "UserModel":
        return UserModel(name=user.name, email=user.email)

class PostgresUserRepository(Repository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[User]:
        instance = self.session.query(UserModel).get(id)
        return instance.to_entity() if instance else None

    def get_all(self) -> List[User]:
        instances = self.session.query(UserModel).all()
        return [instance.to_entity() for instance in instances]

    def create(self, entity: User) -> User:
        instance = UserModel.from_entity(entity)
        self.session.add(instance)
        self.session.commit()
        return instance.to_entity()

    def update(self, id: int, entity: User) -> User:
        instance = self.session.query(UserModel).get(id)
        if not instance:
            raise ValueError("Entity not found")
        instance.name = entity.name
        instance.email = entity.email
        self.session.commit()
        return instance.to_entity()

    def delete(self, id: int) -> bool:
        instance = self.session.query(UserModel).get(id)
        if not instance:
            return False
        self.session.delete(instance)
        self.session.commit()
        return True
>>>

---

## 🧪 Testing with TDD

Unit tests ensure all CRUD operations behave as expected.

<<<python
# tests/test_use_cases.py
import pytest
from core.entities import User
from core.use_cases import CRUDService
from core.interfaces import Repository
from typing import List, Optional

class FakeUserRepository(Repository):
    def __init__(self):
        self.data = {}
        self.counter = 1

    def get_by_id(self, id: int) -> Optional[User]:
        return self.data.get(id)

    def get_all(self) -> List[User]:
        return list(self.data.values())

    def create(self, entity: User) -> User:
        entity.id = self.counter
        self.data[self.counter] = entity
        self.counter += 1
        return entity

    def update(self, id: int, entity: User) -> User:
        if id not in self.data:
            raise ValueError("Entity not found")
        entity.id = id
        self.data[id] = entity
        return entity

    def delete(self, id: int) -> bool:
        if id in self.data:
            del self.data[id]
            return True
        return False

def test_create_user():
    repo = FakeUserRepository()
    service = CRUDService(repo)
    user = User(name="Juan", email="juan@example.com")
    created = service.create_entity(user)
    assert created.id is not None
    assert created.name == "Juan"
>>>

---

## 🚀 Integration with Web Frameworks

This module is framework-independent. To expose CRUD functionality via an API, create an adapter in your preferred framework (FastAPI, Django, Flask, etc.).

Example API adapter using FastAPI:

<<<python
# adapters/api_adapter_example.py
from fastapi import FastAPI, Depends
from core.use_cases import CRUDService
from adapters.repository_postgresql import PostgresUserRepository
from core.entities import User
from sqlalchemy.orm import Session
from database import get_db  # Function to obtain a SQLAlchemy session

app = FastAPI()
repository = PostgresUserRepository(get_db())
service = CRUDService(repository)

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return service.get_entity(user_id)

@app.post("/users/")
def create_user(name: str, email: str):
    user = User(id=None, name=name, email=email)
    return service.create_entity(user)
>>>

---

## 📜 License

This project is open-source and free to use. Contributions are welcome!

---

## 📌 Conclusion

This CRUD module provides a **robust, reusable, and decoupled** foundation for web applications, leveraging **Hexagonal Architecture** and **TDD**. Feel free to extend it with additional entities, adapters, and tests!

**Happy coding!** 🚀
