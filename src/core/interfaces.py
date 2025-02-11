# core/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities import Entity, User

class Repository(ABC):
    """
    Interfaz genérica para un repositorio CRUD.
    """

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Entity]:
        pass

    @abstractmethod
    def get_all(self) -> List[Entity]:
        pass

    @abstractmethod
    def create(self, entity: Entity) -> Entity:
        pass

    @abstractmethod
    def update(self, entity_id: str, entity: Entity) -> Entity:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass
    
    
class InMemoryRepository(Repository):
    def __init__(self):
        self.storage = {}

    def get_by_id(self, entity_id: str) -> Optional[User]:
        return self.storage.get(entity_id)

    def get_all(self) -> List[User]:
        return list(self.storage.values())

    def create(self, entity: User) -> User:
        self.storage[entity.id] = entity
        return entity

    def update(self, entity_id: str, entity: User) -> User:
        if entity_id in self.storage:
            self.storage[entity_id] = entity
            return entity
        raise ValueError("Entity not found")

    def delete(self, entity_id: str) -> bool:
        if entity_id in self.storage:
            del self.storage[entity_id]
            return True
        return False

