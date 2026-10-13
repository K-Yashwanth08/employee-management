def test_create_and_list_roles(client):
    response = client.post("/roles", json={"name": "Analyst"})
    assert response.status_code == 201

    duplicate = client.post("/roles", json={"name": "Analyst"})
    assert duplicate.status_code == 409

    listing = client.get("/roles")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1


def test_get_missing_role(client):
    assert client.get("/roles/999").status_code == 404
