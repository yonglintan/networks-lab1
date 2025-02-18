import httpx
import os
import pytest
from datetime import date

BASE_URL = os.getenv("BASE_URL", "http://localhost:80")

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client


def test_get_no_params(client):
    """Test get request with no query params"""
    response = client.get("/tasks")
    assert response.status_code == 200
    print(response.json())


def test_get_sortby(client):
    """Test get request sorted by id"""
    params = {"sortBy" : "id"}
    response = client.get("/tasks", params=params)
    assert response.status_code == 200
    print(response.json())

    tasks = response.json()
    ids = [t["id"] for t in tasks]
    assert ids == sorted(ids)


def test_get_count(client):
    """Test get request with count query"""
    count_q = 3
    params = {"count" : count_q}
    response = client.get("/tasks", params=params)
    assert response.status_code == 200
    print(response.json())

    tasks = response.json()
    assert len(tasks) == count_q


def test_get_sortby_count(client):
    """Test get request with both sortby and count queries"""
    count_q = 3
    params = {"count" : count_q, "sortBy" : "id"}
    response = client.get("/tasks", params=params)
    assert response.status_code == 200
    print(response.json())

    tasks = response.json()
    ids = [t["id"] for t in tasks]
    assert ids == sorted(ids)
    assert len(tasks) == count_q


def test_post(client):
    """Test post request success"""
    new_task = {
        "title" : "This is a new task",
        "due" : date.today().isoformat()
    }
    r1 = client.post("/tasks", json=new_task)
    assert r1.status_code == 201

    r2 = client.get("/tasks")
    assert r2.status_code == 200
    print(r2.json())

    tasks = r2.json()
    assert any(task["title"] == new_task["title"] and task["due"] == new_task["due"] for task in tasks)


def test_post_fail(client):
    """Test post request fail on invalid input data"""
    new_task = {
        "randomfield" : "This should fail",
        "due" : "not a date"
    }
    resp = client.post("/tasks", json=new_task)
    assert resp.status_code >= 400 and resp.status_code < 500


def test_put(client):
    """Test put request success"""
    id_to_modify = 0
    changed = {
        "title" : "The task has been modified",
        "completed" : True,
        "due" : date.today().isoformat()
    }
    r1 = client.put(f"/tasks/{id_to_modify}", json=changed)
    assert r1.status_code == 200

    r2 = client.get("/tasks")
    assert r2.status_code == 200
    print(r2.json())

    tasks = r2.json()
    task = {}
    for task in tasks:
        if task["id"] == id_to_modify:
            break
    assert all(task[k] == changed[k] for k in changed)


def test_put_fail(client):
    """Test put request fail on nonexistent id"""
    changed = {
        "title" : "The task has been modified",
        "completed" : True,
        "due" : date.today().isoformat()
    }
    resp = client.put("/tasks/-1", json=changed)
    assert resp.status_code >= 400 and resp.status_code < 500

