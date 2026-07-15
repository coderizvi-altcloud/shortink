import asgi_lifespan
import fastapi
import httpx
import pytest
import pytest_asyncio

from backend.source.api.routes.shortlink_routes import repository
from backend.source.config import get_redis_client
from backend.source.main import initialize_backend_application


class _FakePipeline:
    def __init__(self, client: "FakeRedis"):
        self.client = client

    def hset(self, key: str, mapping: dict[str, str]):
        self.client.hset(key, mapping=mapping)
        return self

    def set(self, key: str, value):
        self.client.set(key, value)
        return self

    def zadd(self, key: str, mapping: dict[str, int]):
        self.client.zadd(key, mapping)
        return self

    def delete(self, *keys: str):
        self.client.delete(*keys)
        return self

    def zrem(self, key: str, *members: str):
        self.client.zrem(key, *members)
        return self

    def execute(self):
        return None


class FakeRedis:
    def __init__(self):
        self.values: dict[str, str] = {}
        self.hashes: dict[str, dict[str, str]] = {}
        self.zsets: dict[str, dict[str, int]] = {}
        self.expiries: dict[str, int] = {}

    def flush(self):
        self.values.clear()
        self.hashes.clear()
        self.zsets.clear()
        self.expiries.clear()

    def pipeline(self):
        return _FakePipeline(self)

    def ping(self):
        return True

    def expire(self, key: str, ttl: int):
        self.expiries[key] = ttl
        return True

    def exists(self, key: str) -> bool:
        return key in self.values or key in self.hashes or key in self.zsets

    def get(self, key: str):
        return self.values.get(key)

    def set(self, key: str, value):
        self.values[key] = str(value)
        return True

    def incr(self, key: str):
        current = int(self.values.get(key, "0")) + 1
        self.values[key] = str(current)
        return current

    def delete(self, *keys: str):
        removed = 0
        for key in keys:
            if key in self.values:
                del self.values[key]
                removed += 1
            if key in self.hashes:
                del self.hashes[key]
                removed += 1
            if key in self.zsets:
                del self.zsets[key]
                removed += 1
            if key in self.expiries:
                del self.expiries[key]
        return removed

    def hset(self, key: str, mapping: dict[str, str]):
        self.hashes.setdefault(key, {}).update({k: str(v) for k, v in mapping.items()})
        return True

    def hgetall(self, key: str):
        return dict(self.hashes.get(key, {}))

    def hincrby(self, key: str, field: str, amount: int):
        current = int(self.hashes.setdefault(key, {}).get(field, "0")) + amount
        self.hashes[key][field] = str(current)
        return current

    def zadd(self, key: str, mapping: dict[str, int]):
        self.zsets.setdefault(key, {}).update({member: int(score) for member, score in mapping.items()})
        return True

    def zrevrange(self, key: str, start: int, end: int):
        members = sorted(self.zsets.get(key, {}).items(), key=lambda item: item[1], reverse=True)
        values = [member for member, _ in members]
        if end == -1:
            return values[start:]
        return values[start : end + 1]

    def zrem(self, key: str, *members: str):
        zset = self.zsets.get(key)
        if not zset:
            return 0
        removed = 0
        for member in members:
            if member in zset:
                del zset[member]
                removed += 1
        return removed

    def scan_iter(self, pattern: str):
        prefix = pattern.rstrip("*")
        for key in list(self.values) + list(self.hashes) + list(self.zsets):
            if key.startswith(prefix):
                yield key


@pytest.fixture(name="backend_test_app")
def backend_test_app() -> fastapi.FastAPI:
    app = initialize_backend_application()
    fake_redis = FakeRedis()
    app.state.fake_redis = fake_redis
    app.dependency_overrides[get_redis_client] = lambda: fake_redis
    return app


@pytest.fixture(autouse=True)
def clean_redis_namespace(backend_test_app: fastapi.FastAPI) -> None:
    backend_test_app.state.fake_redis.flush()
    repository.clear_namespace(backend_test_app.state.fake_redis)


@pytest_asyncio.fixture(name="initialize_backend_test_application")
async def initialize_backend_test_application(backend_test_app: fastapi.FastAPI) -> fastapi.FastAPI:
    async with asgi_lifespan.LifespanManager(backend_test_app):
        yield backend_test_app


@pytest_asyncio.fixture(name="async_client")
async def async_client(initialize_backend_test_application: fastapi.FastAPI) -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=initialize_backend_test_application),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest_asyncio.fixture(name="auth_client")
async def auth_client(initialize_backend_test_application: fastapi.FastAPI) -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=initialize_backend_test_application),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        resp = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
            },
        )
        token = resp.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
