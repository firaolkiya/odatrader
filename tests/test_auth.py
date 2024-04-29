import pytest
import time
from backend.auth.jwt_handler import create_token, verify_token

class TestJWT:
    def test_create_token(self):
        t = create_token("user1")
        assert isinstance(t, str)
        assert len(t.split(".")) == 3

    def test_verify_valid(self):
        t = create_token("user1")
        data = verify_token(t)
        assert data["sub"] == "user1"

    def test_verify_invalid(self):
        with pytest.raises(ValueError):
            verify_token("invalid.token.here")

    def test_expired_token(self):
        t = create_token("user1", expires_in=-10)
        with pytest.raises(ValueError):
            verify_token(t)

    def test_app_name_in_payload(self):
        t = create_token("user1")
        data = verify_token(t)
        assert data.get("app") == "OdaTrade"

    @pytest.mark.parametrize("user", ["admin","trader","viewer","bot1"])
    def test_multiple_users(self, user):
        t = create_token(user)
        assert verify_token(t)["sub"] == user
