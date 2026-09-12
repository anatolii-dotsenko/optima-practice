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


def test_create_menu_item_authorized(client, auth_headers, sample_category):
    payload = {
        "category_id": sample_category.id,
        "name": "Американо",
        "price": "50.00",
        "description": "Класичний чорний",
        "is_available": True,
    }
    response = client.post("/api/v1/menu/items", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Американо"
