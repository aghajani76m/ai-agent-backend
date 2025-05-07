def test_ten_rounds_and_token_usage(client):
    # ایجاد یک agent و یک conversation
    ag = client.post("/api/v1/agents", json={"name":"Bot","responseSettings":{}}).json()
    cid = client.post("/api/v1/conversations", json={"agent_id": ag["id"]}).json()["id"]

    # شبیه‌سازی ۱۰ دور مکالمه
    for i in range(10):
        resp = client.post(
            f"/api/v1/conversations/{cid}/messages",
            json={"content": f"hello {i}", "attachments": []}
        )
        body = resp.json()
        msgs = body["messages"]
        # پس از هر بار، messages حداقل 2*i+1 پیام دارد
        assert len(msgs) >= 2 * (i + 1) - 1
        # بررسی وجود token_usage در پیام assistant آخر
        last = msgs[-1]
        if last["role"] == "assistant":
            assert "token_usage" in last
            assert last["token_usage"]["total_tokens"] >= 0

    # در نهایت مطمئن شویم که کل پیام‌ها (۲۰ پیام) برگشت می‌کنند
    final = client.get(f"/api/v1/conversations/{cid}/messages").json()
    assert len(final) >= 20