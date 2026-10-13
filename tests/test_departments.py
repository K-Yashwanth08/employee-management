def test_create_and_list_departments(client):
    response = client.post("/departments", json={"name": "People"})
    assert response.status_code == 201
    department_id = response.json()["id"]

    retrieved = client.get(f"/departments/{department_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["name"] == "People"

    duplicate = client.post("/departments", json={"name": "People"})
    assert duplicate.status_code == 409

    listing = client.get("/departments")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1


def test_department_bad_input_and_missing_resource(client):
    invalid = client.post("/departments", json={"name": "   "})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["message"] == "Validation failed"

    missing = client.get("/departments/999")
    assert missing.status_code == 404
    assert missing.json() == {
        "error": {"code": "404", "message": "Department not found"}
    }


def test_department_employee_endpoint_validates_department_and_pagination(client):
    missing = client.get("/departments/999/employees")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "404"

    department = client.post("/departments", json={"name": "People"}).json()
    invalid_page = client.get(f"/departments/{department['id']}/employees?page=0")
    assert invalid_page.status_code == 422
    assert invalid_page.json()["error"]["code"] == "422"


def test_department_employees(client, seeded_org):
    department_id = seeded_org["department"]["id"]
    role_id = seeded_org["role"]["id"]
    client.post(
        "/employees",
        json={
            "employee_code": "EMP-100",
            "first_name": "John",
            "last_name": "Stone",
            "work_email": "john.stone@example.com",
            "joining_date": "2024-02-01",
            "department_id": department_id,
            "role_id": role_id,
        },
    )

    response = client.get(f"/departments/{department_id}/employees")
    assert response.status_code == 200
    assert response.json()["total"] == 1
