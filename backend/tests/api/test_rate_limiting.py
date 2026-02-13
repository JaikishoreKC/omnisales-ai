import os
import pytest


@pytest.mark.skipif(
    os.getenv("RUN_RATE_LIMIT_TESTS") != "1",
    reason="Rate limit tests can be flaky; enable with RUN_RATE_LIMIT_TESTS=1"
)
def test_chat_rate_limit_enforced(client, user_token_headers, chat_payload, mock_chat_dependencies):
    # Chat is limited to 20/min; send 25 to trigger 429
    for _ in range(25):
        response = client.post("/chat", headers=user_token_headers, json=chat_payload)
        if response.status_code == 429:
            assert response.json()["success"] is False
            return
    pytest.fail("Rate limit was not enforced")
