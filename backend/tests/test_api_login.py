from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.entities import User

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_login_returns_token_and_role():
    with TestingSession() as db:
        db.query(User).delete()
        db.add(User(username="reviewer", password_hash=hash_password("secret123"), role="VIEWER"))
        db.commit()

    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={"username": "reviewer", "password": "secret123"})

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "VIEWER"
    assert body["access_token"]
    assert body["token_type"] == "bearer"
