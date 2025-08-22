from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_docs():
    r = client.get("/docs/nonexistent", headers={"X-API-Key":"dev-secret"})
    assert r.status_code == 200
