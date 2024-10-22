from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_request_password_reset():
    response = client.get("/request_password_reset/invalidemail@email.com")
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid Credentials"}

def test_reset_password():
    response = client.put("/reset-password", json={"code": "wrongcode","password":"rampass"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid Password Reset Code"}