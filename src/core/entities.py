from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class Entity:
    """
    Clase base genérica para las entidades.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True
    deleted: bool = False
    
@dataclass
class User(Entity):
    name: str = field(default="")
    email: str = field(default="")