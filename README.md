# My CRUD Module Template with Hexagonal Architecture and TDD

This repository provides a generic CRUD module built in Python using Hexagonal Architecture and Test-Driven Development (TDD). It is designed to serve as a modular template for future projects, regardless of the specific web framework or technology stack. The core domain is independent of infrastructure details, making it reusable for various CRUD implementations (e.g., users, products, blogs, multimedia).

---

## Project Structure

The repository is organized as follows:

>>> 
my_crud_module/
├── core/                      # Domain and business logic
│   ├── __init__.py
│   ├── entities.py            # Generic entities (e.g., User, Product)
│   ├── interfaces.py          # Ports: Repository interfaces and others
│   └── use_cases.py           # Use cases / services implementing CRUD
├── adapters/                  # Adapters for infrastructure (e.g., persistence, APIs)
│   ├── __init__.py
│   ├── repository_postgresql.py  # PostgreSQL-specific adapter
│   └── api_adapter_example.py     # (Optional) API adapter for web frameworks
├── tests/                     # Automated tests (TDD)
│   ├── __init__.py
│   ├── test_use_cases.py
│   └── test_repository_postgresql.py  # (Optional) Integration tests for PostgreSQL adapter
├── requirements.txt           # Dependencies (e.g., SQLAlchemy, pytest)
└── README.md                  # This documentation file
>>>

---

## Domain and Core

### Entities

The entities are defined as plain data classes that represent the business objects. For example, a generic entity and a concrete User entity are defined as follows:

>>>python
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

### Repository Interface (Ports)

The repository interface defines the minimal CRUD operations that any persistence adapter must implement.

>>>python
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

### Use Cases (CRUD Service)

The CRUD service encapsulates the business logic and uses the repository interface for persistence.

>>>python
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

## Adapters

### PostgreSQL Adapter

This adapter implements the repository interface using SQLAlchemy for PostgreSQL.

>>>python
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

## Testing (TDD)

Tests are written first to ensure that each CRUD operation works as expected. Below is an example using a fake repository for testing the core CRUD service.

>>>python
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

def test_get_user():
    repo = FakeUserRepository()
    service = CRUDService(repo)
    user = User(name="Juan", email="juan@example.com")
    created = service.create_entity(user)
    retrieved = service.get_entity(created.id)
    assert retrieved == created

def test_update_user():
    repo = FakeUserRepository()
    service = CRUDService(repo)
    user = User(name="Juan", email="juan@example.com")
    created = service.create_entity(user)
    updated_user = User(name="Juan Updated", email="juan.updated@example.com")
    service.update_entity(created.id, updated_user)
    retrieved = service.get_entity(created.id)
    assert retrieved.name == "Juan Updated"

def test_delete_user():
    repo = FakeUserRepository()
    service = CRUDService(repo)
    user = User(name="Juan", email="juan@example.com")
    created = service.create_entity(user)
    result = service.delete_entity(created.id)
    assert result is True
    assert service.get_entity(created.id) is None
>>>

---

## Integration with Web Frameworks

This core module is independent of any web framework. To integrate with a specific framework, create an adapter (for example, using FastAPI, Django, or Flask) that exposes the CRUD operations via an API.

Below is an example of an API adapter using FastAPI:

>>>python
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

## Conclusion

This modular CRUD template, built with Hexagonal Architecture and TDD in Python, provides a robust and reusable foundation for developing web applications. It decouples the core business logic from infrastructure details, allowing you to easily integrate it into various projects with different technologies and frameworks.

Feel free to extend this template by adding more entities, adapters, and tests as needed.

Happy coding!
