def test_login_mauvais_mot_de_passe(client):
    response = client.post("/auth/login", data={
        "username": "email_qui_nexiste_pas@test.com",
        "password": "mauvais_mot_de_passe",
    })
    assert response.status_code == 401

def test_me_sans_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401