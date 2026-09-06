from app.core.permissions import Perfil


def test_login_valido_retorna_token(client, db):
    from app.core.security import hash_senha
    from app.models.usuario import Usuario

    db.add(Usuario(nome="Teste", login="teste1", senha_hash=hash_senha("abc123"), perfil=Perfil.OPERADOR))
    db.commit()

    resposta = client.post("/api/v1/auth/login", json={"login": "teste1", "senha": "abc123"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["access_token"]
    assert corpo["usuario"]["login"] == "teste1"


def test_login_senha_invalida(client, db):
    from app.core.security import hash_senha
    from app.models.usuario import Usuario

    db.add(Usuario(nome="Teste", login="teste2", senha_hash=hash_senha("abc123"), perfil=Perfil.OPERADOR))
    db.commit()

    resposta = client.post("/api/v1/auth/login", json={"login": "teste2", "senha": "errada"})

    assert resposta.status_code == 401
    assert resposta.json()["code"] == "CREDENCIAIS_INVALIDAS"


def test_me_sem_token(client):
    resposta = client.get("/api/v1/auth/me")
    assert resposta.status_code == 401


def test_me_com_token(client, auth_headers):
    headers = auth_headers(Perfil.GESTOR_QUALIDADE)
    resposta = client.get("/api/v1/auth/me", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["perfil"] == Perfil.GESTOR_QUALIDADE.value
