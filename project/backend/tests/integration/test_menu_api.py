def test_get_categories_empty_and_populated(client, sample_category):
    response = client.get("/api/v1/menu/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Кава"
    assert data[0]["slug"] == "coffee"


def test_get_menu_items_filtering(client, sample_menu_item, unavailable_menu_item):
    # Public gets available only
    response = client.get("/api/v1/menu/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Капучино"

    # Search filter
    resp_search = client.get("/api/v1/menu/items?search=Капучино")
    assert resp_search.status_code == 200
    assert len(resp_search.json()) == 1


def test_get_single_menu_item(client, sample_menu_item):
    response = client.get(f"/api/v1/menu/items/{sample_menu_item.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Капучино"

    not_found = client.get("/api/v1/menu/items/999999")
    assert not_found.status_code == 404
    assert not_found.json()["code"] == "menu_item_not_found"


def test_create_menu_item_authorized(client, auth_headers, admin_headers, sample_category):
    payload = {
        "category_id": sample_category.id,
        "name": "Американо",
        "price": "50.00",
        "description": "Класичний чорний",
        "is_available": True,
    }
    # Regular customer cannot create menu items (HTTP 403)
    resp_forbidden = client.post("/api/v1/menu/items", json=payload, headers=auth_headers)
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["code"] == "forbidden"

    # Admin user can create menu items (HTTP 201)
    response = client.post("/api/v1/menu/items", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Американо"


def test_update_menu_item_admin(client, auth_headers, admin_headers, sample_menu_item):
    update_payload = {"price": "85.00", "description": "Новий смак"}

    # Customer gets 403
    forbidden = client.put(
        f"/api/v1/menu/items/{sample_menu_item.id}", json=update_payload, headers=auth_headers
    )
    assert forbidden.status_code == 403

    # Admin gets 200
    res = client.put(
        f"/api/v1/menu/items/{sample_menu_item.id}", json=update_payload, headers=admin_headers
    )
    assert res.status_code == 200
    assert float(res.json()["price"]) == 85.00
    assert res.json()["description"] == "Новий смак"


def test_toggle_item_availability_admin(client, auth_headers, admin_headers, sample_menu_item):
    # Customer gets 403
    forbidden = client.patch(
        f"/api/v1/menu/items/{sample_menu_item.id}/availability",
        json={"is_available": False},
        headers=auth_headers,
    )
    assert forbidden.status_code == 403

    # Admin sets out of stock
    res = client.patch(
        f"/api/v1/menu/items/{sample_menu_item.id}/availability",
        json={"is_available": False},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["is_available"] is False

    # Check public menu excludes it when available_only=True
    public_res = client.get("/api/v1/menu/items?available_only=true")
    assert not any(i["id"] == sample_menu_item.id for i in public_res.json())


def test_delete_menu_item_admin(client, auth_headers, admin_headers, sample_menu_item):
    # Customer gets 403
    forbidden = client.delete(f"/api/v1/menu/items/{sample_menu_item.id}", headers=auth_headers)
    assert forbidden.status_code == 403

    # Admin deletes item
    del_res = client.delete(f"/api/v1/menu/items/{sample_menu_item.id}", headers=admin_headers)
    assert del_res.status_code == 204

    # Item no longer exists
    get_res = client.get(f"/api/v1/menu/items/{sample_menu_item.id}")
    assert get_res.status_code == 404


def test_category_management_admin(client, auth_headers, admin_headers):
    cat_payload = {
        "name": "Сезонні напої",
        "slug": "seasonal",
        "description": "Осінні пряні напої",
        "display_order": 10,
    }

    # Customer cannot create category (403)
    forbidden = client.post("/api/v1/menu/categories", json=cat_payload, headers=auth_headers)
    assert forbidden.status_code == 403

    # Admin creates category
    create_res = client.post("/api/v1/menu/categories", json=cat_payload, headers=admin_headers)
    assert create_res.status_code == 201
    cat_id = create_res.json()["id"]
    assert create_res.json()["slug"] == "seasonal"

    # Admin updates category
    update_res = client.put(
        f"/api/v1/menu/categories/{cat_id}",
        json={"name": "Осінні напої"},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Осінні напої"

    # Admin deletes category
    del_res = client.delete(f"/api/v1/menu/categories/{cat_id}", headers=admin_headers)
    assert del_res.status_code == 204
