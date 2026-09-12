def test_create_order_unauthorized(client, sample_menu_item):
    response = client.post(
        "/api/v1/orders",
        json={"items": [{"menu_item_id": sample_menu_item.id, "quantity": 1}]},
    )
    assert response.status_code == 401


def test_create_order_success(client, auth_headers, sample_menu_item):
    payload = {
        "items": [{"menu_item_id": sample_menu_item.id, "quantity": 2}],
        "notes": "Без цукру",
    }
    response = client.post("/api/v1/orders", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == "130.00"
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["unit_price"] == "65.00"


def test_create_order_unavailable_item_returns_400(client, auth_headers, unavailable_menu_item):
    payload = {
        "items": [{"menu_item_id": unavailable_menu_item.id, "quantity": 1}],
    }
    response = client.post("/api/v1/orders", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["code"] == "menu_item_unavailable"


def test_create_order_empty_items_returns_422(client, auth_headers):
    response = client.post("/api/v1/orders", json={"items": []}, headers=auth_headers)
    assert response.status_code == 422


def test_list_and_get_user_orders(client, auth_headers, sample_menu_item):
    # Place order
    client.post(
        "/api/v1/orders",
        json={"items": [{"menu_item_id": sample_menu_item.id, "quantity": 1}]},
        headers=auth_headers,
    )

    # List orders
    list_resp = client.get("/api/v1/orders", headers=auth_headers)
    assert list_resp.status_code == 200
    orders = list_resp.json()
    assert len(orders) >= 1
    order_id = orders[0]["id"]

    # Get single order
    get_resp = client.get(f"/api/v1/orders/{order_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == order_id


def test_update_order_status_lifecycle(client, auth_headers, sample_menu_item):
    create_resp = client.post(
        "/api/v1/orders",
        json={"items": [{"menu_item_id": sample_menu_item.id, "quantity": 1}]},
        headers=auth_headers,
    )
    order_id = create_resp.json()["id"]

    # PENDING -> CONFIRMED
    patch_resp = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "confirmed"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "confirmed"

    # CONFIRMED -> CANCELLED
    cancel_resp = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "cancelled"},
        headers=auth_headers,
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # CANCELLED -> READY (illegal transition from terminal state)
    illegal_resp = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "ready"},
        headers=auth_headers,
    )
    assert illegal_resp.status_code == 400
    assert illegal_resp.json()["code"] == "invalid_state_transition"
