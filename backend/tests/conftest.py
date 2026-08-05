import os
os.environ["DATABASE_URL"]="sqlite+pysqlite:///./test_ruwi.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine
from app.seed import run
import pytest
@pytest.fixture(scope="session",autouse=True)
def setup():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine);run();yield;Base.metadata.drop_all(engine)
@pytest.fixture
def client(): return TestClient(app,raise_server_exceptions=False)
@pytest.fixture
def token(client): return client.post('/api/v1/auth/login',json={'email':'visitor@example.com','password':'Visitor123!'}).json()['access_token']
@pytest.fixture
def curator_token(client): return client.post('/api/v1/auth/login',json={'email':'curator@example.com','password':'Curator123!'}).json()['access_token']
@pytest.fixture
def admin_token(client): return client.post('/api/v1/auth/login',json={'email':'admin@example.com','password':'Admin123!'}).json()['access_token']
