from datetime import date, timedelta


def employee_payload(seeded_org, **overrides):
    payload = {
        "employee_code": "EMP-200",
        "first_name": "Avery",
        "last_name": "Morgan",
        "work_email": "avery.morgan@example.com",
        "phone": "+1-555-0100",
        "joining_date": "2024-03-01",
        "department_id": seeded_org["department"]["id"],
        "role_id": seeded_org["role"]["id"],
        "manager_id": None,
    }
    payload.update(overrides)
    return payload


def test_employee_create_retrieve_update_and_soft_delete(client, seeded_org):
    created = client.post("/employees", json=employee_payload(seeded_org))
    assert created.status_code == 201
    employee_id = created.json()["id"]

    retrieved = client.get(f"/employees/{employee_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["employee_code"] == "EMP-200"

    updated = client.patch(f"/employees/{employee_id}", json={"phone": None, "last_name": "Reed"})
    assert updated.status_code == 200
    assert updated.json()["phone"] is None
    assert updated.json()["last_name"] == "Reed"

    deleted = client.delete(f"/employees/{employee_id}")
    assert deleted.status_code == 204
    assert client.get(f"/employees/{employee_id}").status_code == 404


def test_pagination_filtering_and_search_together(client, seeded_org):
    dep_id = seeded_org["department"]["id"]
    role_id = seeded_org["role"]["id"]
    for index, first_name in enumerate(["John", "Joanna", "Jordan", "Alex"], start=1):
        client.post(
            "/employees",
            json=employee_payload(
                seeded_org,
                employee_code=f"EMP-30{index}",
                first_name=first_name,
                last_name="Smith",
                work_email=f"{first_name.lower()}.smith@example.com",
            ),
        )

    response = client.get(f"/employees?page=2&size=1&department={dep_id}&q=jo")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["page"] == 2
    assert body["size"] == 1
    assert body["total_pages"] == 3
    assert body["items"][0]["first_name"] == "Joanna"
    assert body["items"][0]["role"]["id"] == role_id


def test_direct_reports(client, seeded_org):
    manager = client.post("/employees", json=employee_payload(seeded_org, employee_code="EMP-401")).json()
    report = client.post(
        "/employees",
        json=employee_payload(
            seeded_org,
            employee_code="EMP-402",
            first_name="Taylor",
            work_email="taylor.report@example.com",
            manager_id=manager["id"],
        ),
    )
    assert report.status_code == 201

    team = client.get(f"/employees/{manager['id']}/team")
    assert team.status_code == 200
    assert len(team.json()) == 1


def test_invalid_inputs(client, seeded_org):
    bad_email = client.post("/employees", json=employee_payload(seeded_org, work_email="not-an-email"))
    assert bad_email.status_code == 422
    assert bad_email.json()["error"]["code"] == "422"
    assert bad_email.json()["error"]["message"] == "Validation failed"

    empty_name = client.post("/employees", json=employee_payload(seeded_org, first_name="   "))
    assert empty_name.status_code == 422

    future_date = (date.today() + timedelta(days=1)).isoformat()
    future = client.post("/employees", json=employee_payload(seeded_org, joining_date=future_date))
    assert future.status_code == 422


def test_update_rejects_null_required_fields(client, seeded_org):
    employee = client.post("/employees", json=employee_payload(seeded_org)).json()

    response = client.patch(f"/employees/{employee['id']}", json={"department_id": None})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "422"


def test_employee_not_found_errors_share_format(client):
    response = client.get("/employees/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "404", "message": "Employee not found"}
    }


def test_employee_list_rejects_invalid_pagination(client):
    response = client.get("/employees?page=0&size=101")

    assert response.status_code == 422
    assert response.json()["error"]["message"] == "Validation failed"


def test_missing_refs_and_duplicates(client, seeded_org):
    missing_department = client.post("/employees", json=employee_payload(seeded_org, department_id=999))
    assert missing_department.status_code == 422

    first = client.post("/employees", json=employee_payload(seeded_org))
    assert first.status_code == 201

    duplicate_email = client.post(
        "/employees",
        json=employee_payload(
            seeded_org,
            employee_code="EMP-201",
            work_email="avery.morgan@example.com",
        ),
    )
    assert duplicate_email.status_code == 409

    duplicate_code = client.post(
        "/employees",
        json=employee_payload(
            seeded_org,
            employee_code="EMP-200",
            work_email="avery.other@example.com",
        ),
    )
    assert duplicate_code.status_code == 409
