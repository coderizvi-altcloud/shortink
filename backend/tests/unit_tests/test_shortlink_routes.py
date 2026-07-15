import pytest


@pytest.mark.asyncio
async def test_create_shortlink_returns_short_url(auth_client):
    response = await auth_client.post("/shortlinks", json={"url": "https://example.com"})

    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://example.com"
    assert body["click_count"] == 0
    assert len(body["short_code"]) == 5


@pytest.mark.asyncio
async def test_unauthenticated_request_returns_403(async_client):
    response = await async_client.post("/shortlinks", json={"url": "https://example.com"})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_get_update_delete_shortlink(auth_client):
    created = await auth_client.post("/shortlinks", json={"url": "https://example.org"})
    shortlink_id = created.json()["id"]
    short_code = created.json()["short_code"]

    listed = await auth_client.get("/shortlinks")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = await auth_client.get(f"/shortlinks/{shortlink_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == shortlink_id

    updated = await auth_client.put(
        f"/shortlinks/{shortlink_id}",
        json={"short_code": "abc12345"},
    )
    assert updated.status_code == 200
    assert updated.json()["short_code"] == "abc12345"

    deleted = await auth_client.delete(f"/shortlinks/{shortlink_id}")
    assert deleted.status_code == 204

    missing = await auth_client.get(f"/shortlinks/{shortlink_id}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_update_shortlink_rejects_empty_payload(auth_client):
    created = await auth_client.post("/shortlinks", json={"url": "https://example.org"})
    shortlink_id = created.json()["id"]

    response = await auth_client.put(f"/shortlinks/{shortlink_id}", json={})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_missing_shortlink_returns_404(auth_client):
    assert (await auth_client.get("/shortlinks/999999")).status_code == 404
    assert (await auth_client.put("/shortlinks/999999", json={"short_code": "abc12345"})).status_code == 404
    assert (await auth_client.delete("/shortlinks/999999")).status_code == 404
    assert (await auth_client.get("/missing-code", follow_redirects=False)).status_code == 404


@pytest.mark.asyncio
async def test_redirect_shortlink_increments_click_count(auth_client):
    created = await auth_client.post("/shortlinks", json={"url": "https://example.net"})
    short_code = created.json()["short_code"]

    redirect = await auth_client.get(f"/{short_code}", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://example.net"

    tiny = await auth_client.get(f"/s/{short_code}", follow_redirects=False)
    assert tiny.status_code == 307

    legacy = await auth_client.get(f"/r/{short_code}", follow_redirects=False)
    assert legacy.status_code == 307

    fetched = await auth_client.get(f"/shortlinks/{created.json()['id']}")
    assert fetched.json()["click_count"] == 3


@pytest.mark.asyncio
async def test_register_and_login(auth_client):
    me = await auth_client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "test@example.com"
    assert me.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_wrong_password(initialize_backend_test_application):
    async with __import__("httpx").AsyncClient(
        transport=__import__("httpx").ASGITransport(app=initialize_backend_test_application),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        await client.post(
            "/auth/register",
            json={"email": "login@example.com", "username": "loginuser", "password": "correctpass"},
        )
        resp = await client.post(
            "/auth/login",
            json={"email": "login@example.com", "password": "wrongpass"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_email_rejected(initialize_backend_test_application):
    async with __import__("httpx").AsyncClient(
        transport=__import__("httpx").ASGITransport(app=initialize_backend_test_application),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        await client.post(
            "/auth/register",
            json={"email": "dup@example.com", "username": "user1", "password": "pass123"},
        )
        resp = await client.post(
            "/auth/register",
            json={"email": "dup@example.com", "username": "user2", "password": "pass123"},
        )
        assert resp.status_code == 400
