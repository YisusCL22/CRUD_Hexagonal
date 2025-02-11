import pytest
from core.entities import User
from core.interfaces import InMemoryRepository
from core.use_cases import CRUDService

@pytest.fixture
def repository():
    return InMemoryRepository()

@pytest.fixture
def crud_service(repository):
    return CRUDService(repository)

def test_create_user(crud_service):
    user = User(name="John Doe", email="john.doe@example.com")
    created_user = crud_service.create(user)
    assert created_user.id is not None
    assert created_user.name == "John Doe"
    assert created_user.email == "john.doe@example.com"

def test_get_user(crud_service):
    user = User(name="Jane Doe", email="jane.doe@example.com")
    created_user = crud_service.create(user)
    fetched_user = crud_service.get(created_user.id)
    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.name == "Jane Doe"
    assert fetched_user.email == "jane.doe@example.com"

def test_update_user(crud_service):
    user = User(name="John Smith", email="john.smith@example.com")
    created_user = crud_service.create(user)
    created_user.name = "John Smith Updated"
    updated_user = crud_service.update(created_user.id, created_user)
    assert updated_user.name == "John Smith Updated"

def test_delete_user(crud_service):
    user = User(name="Jane Smith", email="jane.smith@example.com")
    created_user = crud_service.create(user)
    delete_result = crud_service.delete(created_user.id)
    assert delete_result is True
    assert crud_service.get(created_user.id) is None