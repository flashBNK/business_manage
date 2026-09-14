import pytest


@pytest.mark.asyncio
async def test_application_responds(client):
    response = await client.get("/api/v1/me")

    assert response.status_code == 401
