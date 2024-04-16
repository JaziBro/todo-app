from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
from fastapi_todo import settings
from fastapi_todo.database import database
from fastapi_todo import settings, main


def create_test_database():
    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg"
    )
    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
    )
    SQLModel.metadata.create_all(engine)
    return engine

def cleanup_database(engine):
    SQLModel.metadata.drop_all(engine)

def override_session_dependency(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session
    main.app.dependency_overrides[database.get_session] = get_session_override

def test_read_main():
    client = TestClient(app=main.app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_write_main():
    engine = create_test_database()
    override_session_dependency(engine)

    try:
        client = TestClient(app=main.app)
        todo_content = "buy bread"
        response = client.post("/todos/", json={"content": todo_content})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["content"] == todo_content
    finally:
        cleanup_database(engine)

def test_read_list_main():
    engine = create_test_database()
    override_session_dependency(engine)

    try:
        client = TestClient(app=main.app)
        response = client.get("/todos/")
        assert response.status_code == 200
    finally:
        cleanup_database(engine)


def test_delete_todo():
    engine = create_test_database()
    override_session_dependency(engine)

    try:
        client = TestClient(app=main.app)
        
        response_create = client.post("/todos/", json={"content": "test todo"})
        assert response_create.status_code == 200
        created_todo_id = response_create.json()["id"]

        response_delete = client.delete(f"/todos/{created_todo_id}")
        assert response_delete.status_code == 200

        response_get = client.get(f"/todos/{created_todo_id}/")
        assert response_get.status_code == 404
    finally:
        cleanup_database(engine)

def test_update_todo():
    engine = create_test_database()
    override_session_dependency(engine)

    try:
        client = TestClient(app=main.app)

        response_create = client.post("/todos/", json={"content": "old todo"})
        assert response_create.status_code == 200
        created_todo_id = response_create.json()["id"]

        new_content = "updated todo"
        response_update = client.put(f"/todos/{created_todo_id}/", json={"content": new_content})
        assert response_update.status_code == 200

        # Ensure that the todo content is updated
        response_get = client.get(f"/todos/{created_todo_id}/")
        assert response_get.status_code == 200
        assert response_get.json()["content"] == new_content
    finally:
        cleanup_database(engine)
