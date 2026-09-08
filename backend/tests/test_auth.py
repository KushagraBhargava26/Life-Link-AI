# backend/tests/test_auth.py
# LifeLink AI — Authentication Test Suite
# Architecture Reference: ARCHITECTURE.md Section 18 & Section 35

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_register_valid_user() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_email = f"donor_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": unique_email,
            "password": "SecurePassword123!",
            "first_name": "Arjun",
            "last_name": "Mehta",
            "phone": "+919876543210",
            "role": "DONOR",
        }
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == unique_email
        assert data["data"]["first_name"] == "Arjun"
        assert "DONOR" in data["data"]["roles"]
        assert "password" not in data["data"]
        assert "password_hash" not in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": unique_email,
            "password": "SecurePassword123!",
            "first_name": "First",
            "last_name": "User",
            "role": "DONOR",
        }
        res1 = await client.post("/api/v1/auth/register", json=payload)
        assert res1.status_code == 201

        # Attempt duplicate
        res2 = await client.post("/api/v1/auth/register", json=payload)
        assert res2.status_code == 409
        data2 = res2.json()
        assert data2["success"] is False
        assert data2["error"]["code"] == "USER_EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_weak_password() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "email": f"weak_{uuid.uuid4().hex[:8]}@example.com",
            "password": "weak",  # No uppercase, digit, special, < 8 chars
            "first_name": "Test",
            "last_name": "User",
            "role": "DONOR",
        }
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False


@pytest.mark.asyncio
async def test_login_success_and_me() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = f"login_{uuid.uuid4().hex[:8]}@example.com"
        password = "ComplexPassword789!"
        # 1. Register
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "first_name": "Kavita",
            "last_name": "Nair",
            "role": "DONOR",
        })
        assert reg_res.status_code == 201

        # 2. Login
        login_res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password,
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["success"] is True
        token = login_data["data"]["access_token"]
        assert token is not None
        assert login_data["data"]["token_type"].lower() == "bearer"

        # 3. Authenticated /me
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["success"] is True
        assert me_data["data"]["email"] == email
        assert me_data["data"]["first_name"] == "Kavita"

        # 4. Logout
        logout_res = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_res.status_code == 200
        assert logout_res.json()["success"] is True


@pytest.mark.asyncio
async def test_login_invalid_password() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = f"inv_{uuid.uuid4().hex[:8]}@example.com"
        await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "CorrectPassword123!",
            "first_name": "Test",
            "last_name": "Pass",
            "role": "DONOR",
        })

        # Wrong password
        response = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "WrongPassword999!",
        })
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_me_unauthenticated() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # No token
        res1 = await client.get("/api/v1/auth/me")
        assert res1.status_code == 401
        assert res1.json()["error"]["code"] == "AUTH_TOKEN_MISSING"

        # Invalid token
        res2 = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer fake.token.here"})
        assert res2.status_code == 401
        assert res2.json()["error"]["code"] == "AUTH_TOKEN_INVALID"
