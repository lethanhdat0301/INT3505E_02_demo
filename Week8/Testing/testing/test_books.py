import json
import pytest
from app import app, db
from models import Book

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_book(client):
    data = {"title": "Python for QA Engineers", "author": "Mike", "category": "Testing"}
    response = client.post('/api/v1/books', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["title"] == "Python for QA Engineers"

def test_get_books(client):
    client.post('/api/v1/books', json={"title": "Flask 101"})
    response = client.get('/api/v1/books')
    assert response.status_code == 200
    json_data = response.get_json()
    assert "data" in json_data

def test_update_book(client):
    post_resp = client.post('/api/v1/books', json={"title": "Old Title"})
    book_id = post_resp.get_json()["id"]
    put_resp = client.put(f'/api/v1/books/{book_id}', json={"title": "New Title"})
    assert put_resp.status_code == 200
    assert put_resp.get_json()["title"] == "New Title"

def test_delete_book(client):
    post_resp = client.post('/api/v1/books', json={"title": "Temp Book"})
    book_id = post_resp.get_json()["id"]
    delete_resp = client.delete(f'/api/v1/books/{book_id}')
    assert delete_resp.status_code == 200
    get_resp = client.get(f'/api/v1/books/{book_id}')
    assert get_resp.status_code == 404

def test_filter_books(client):
    client.post('/api/v1/books', json={"title": "API Testing", "category": "QA"})
    resp = client.get('/api/v1/books?category=QA')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert len(json_data["data"]["items"]) > 0
