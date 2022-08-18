import asyncio
import random
from string import ascii_letters, digits

import bcrypt
import pytest
import pytest_asyncio
from app.db.schema import Base, Users
from app.main import app
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from starlette.testclient import TestClient


class UserClient:
    def __init__(self, client: TestClient = None, user: Users = None) -> None:
        self.client: TestClient = client or TestClient(app)
        self.user: Users = user


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def user_class() -> Users:
    return Users


@pytest_asyncio.fixture(scope="session")
def engine():
    engine = create_async_engine(
        "postgresql+asyncpg://"
    )
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture
async def create(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine, create):
    async with AsyncSession(engine) as session:
        yield session


@pytest_asyncio.fixture
async def async_app_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://localhost:8081") as client:
        yield client


@pytest.fixture
def get_random_pswd() -> str:
    test_pswd = ''
    for _ in range(int('1'+random.choice(digits))):
        test_pswd += random.choice(ascii_letters + digits + '!@#$%^&*()_+,.;')

    hashed_pswd = bcrypt.hashpw(test_pswd.encode('utf-8'), bcrypt.gensalt())
    return hashed_pswd.decode()


@pytest.fixture
def user_1(get_random_pswd) -> Users:
    user = Users(email='testuser_1@gmail.com', nickname='testuser', username='testname', phone='01000000000',
                 pswd=get_random_pswd)
    return user


@pytest.fixture
def user_2(get_random_pswd) -> Users:
    user = Users(email='testuser2@gmail.com', nickname='testuser2', username='testname2', phone='01000000001',
                 pswd=get_random_pswd)
    return user
