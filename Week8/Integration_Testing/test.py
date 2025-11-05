import pytest
import requests
import responses
from book_service import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

@responses.activate
def test_book_calls_user_service(client):
    # Mock UserService API
    responses.add(
        responses.GET,
        "http://localhost:5001/users/1",
        json={"id": 1, "name": "Alice"},
        status=200
    )

    res = client.get("/books/1")
    data = res.get_json()

    assert res.status_code == 200
    assert data["user"]["name"] == "Alice"
    assert "Python 101" in data["title"]
