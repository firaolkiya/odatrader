import pytest

class TestHealthAPI:
    def test_health(self, api_client):
        r = api_client.get("/health/")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_ready(self, api_client):
        r = api_client.get("/health/ready")
        assert r.status_code == 200

class TestStatusAPI:
    def test_status(self, api_client):
        r = api_client.get("/status")
        assert r.status_code == 200
        assert r.json()["service"] == "OdaTrade"

class TestAuthAPI:
    def test_login_success(self, api_client):
        r = api_client.post("/auth/login", json={"username": "admin", "password": "odatrade-admin"})
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_fail(self, api_client):
        r = api_client.post("/auth/login", json={"username": "admin", "password": "wrong"})
        assert r.status_code == 401

    def test_me_authenticated(self, api_client, auth_token):
        r = api_client.get("/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
        assert r.status_code == 200

    def test_me_no_auth(self, api_client):
        r = api_client.get("/auth/me")
        assert r.status_code == 401

class TestInstrumentsAPI:
    def test_list(self, api_client):
        r = api_client.get("/instruments/")
        assert r.status_code == 200
        assert len(r.json()["instruments"]) >= 5

    def test_get_btc(self, api_client):
        r = api_client.get("/instruments/BTCUSDT")
        assert r.status_code == 200

    def test_pair_scores(self, api_client):
        r = api_client.get("/instruments/pairs/scores")
        assert r.status_code == 200

class TestSignalsAPI:
    def test_evaluate(self, api_client):
        r = api_client.get("/signals/evaluate/btcusdt")
        assert r.status_code == 200

class TestConfigAPI:
    def test_get_config(self, api_client):
        r = api_client.get("/config/")
        assert r.status_code == 200

    def test_set_mode(self, api_client, auth_token):
        r = api_client.post("/config/mode?mode=paper", headers={"Authorization": f"Bearer {auth_token}"})
        assert r.status_code == 200

class TestMetricsAPI:
    def test_prometheus(self, api_client):
        r = api_client.get("/metrics/")
        assert r.status_code == 200

    def test_pnl(self, api_client, auth_token):
        r = api_client.get("/metrics/pnl?window=1d", headers={"Authorization": f"Bearer {auth_token}"})
        assert r.status_code == 200

class TestV2API:
    def test_v2_status(self, api_client):
        r = api_client.get("/api/v2/status")
        assert r.status_code == 200
        assert "multi-bot" in r.json()["features"]

class TestStrategyControl:
    def test_start_stop(self, api_client, auth_token):
        h = {"Authorization": f"Bearer {auth_token}"}
        r = api_client.post("/strategy/start", json={"name": "test"}, headers=h)
        assert r.status_code == 200
        r = api_client.post("/strategy/stop", json={"name": "test"}, headers=h)
        assert r.status_code == 200
