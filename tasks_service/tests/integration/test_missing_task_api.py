from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_update_missing_task_returns_404(client, set_auth_token):
    company_id = uuid4()
    task_id = uuid4()
    set_auth_token(company_id)

    response = await client.patch(
        f"/api/v1/companies/{company_id}/tasks/{task_id}",
        json={"title": "Updated task"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}
