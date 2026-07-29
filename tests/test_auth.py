from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

'''def test_diagnostic():
    for route in app.routes:
        if route.path == "/auth/login":
            print("METHODES:", route.methods)

    response = client.post("/auth/login", data={
        "username": "email_qui_nexiste_pas@test.com",
        "password": "mauvais_mot_de_passe"
    })
    print("STATUS:", response.status_code)
    print("BODY:", response.text)'''

def test_login_mauvais_mot_de_passe():
    response = client.post("/auth/login", data={
        "username": "email_qui_nexiste_pas@test.com",
        "password": "mauvais_mot_de_passe"
    })
    assert response.status_code == 401