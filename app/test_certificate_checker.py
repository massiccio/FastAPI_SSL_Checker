from fastapi.testclient import TestClient

from certificate_checker import app

client = TestClient(app)

## pip install requests
## pip install pytest
## pytest

def test_empty():
    response = client.get("/check/")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Not Found'


def test_strip1():
    response = client.get("/check/google.com ")
    assert response.status_code == 200
    res = response.json()
    assert res['isValid'] == True

def test_strip2():
    response = client.get("/check/ google.com")
    assert response.status_code == 200
    res = response.json()
    assert res['isValid'] == True

def test_valid():
    response = client.get("/check/google.com")
    assert response.status_code == 200
    res = response.json()
    assert res['isValid'] == True

def test_self_signed():
    response = client.get("/check/self-signed.badssl.com")
    assert response.status_code == 200
    res = response.json()
    assert res['isValid'] == True

def test_expired():
    response = client.get("/check/expired.badssl.com")
    assert response.status_code == 200
    assert response.json()['isValid'] == False

def test_no_ssl():
    response = client.get("/check/google.local")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Certificate not found'