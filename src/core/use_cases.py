# core/use_cases.py
from typing import List, Optional
from core.entities import Entity
from core.interfaces import Repository

class CRUDService:
    """
    Servicio genérico para operaciones CRUD sobre una entidad.
    """
    def __init__(self, repository: Repository):
        self.repository = repository

    def get(self, entity_id: str) -> Optional[Entity]:
        return self.repository.get_by_id(entity_id)

    def list_all(self) -> List[Entity]:
        return self.repository.get_all()

    def create(self, entity: Entity) -> Entity:
        return self.repository.create(entity)

    def update(self, entity_id: str, entity: Entity) -> Entity:
        return self.repository.update(entity_id, entity)

    def delete(self, entity_id: str) -> bool:
        return self.repository.delete(entity_id)
