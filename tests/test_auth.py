"""
Unit tests for mbse4u_sysmlv2_auth and the authenticated session integration
in mbse4u_sysmlv2_api_helpers.

Run with:
    pip install pytest requests-mock
    pytest test_auth.py -v
"""

import pytest
import requests_mock as req_mock

from mbse4u_sysmlv2_auth import (
    configure_session,
    get_session,
    SysMLV2Error,
    SysMLV2AuthError,
    SysMLV2APIError,
    SysMLV2NotFoundError,
    SysMLV2BadRequestError,
    SysMLV2ConflictError,
)
import mbse4u_sysmlv2_helpers as h

BASE_URL = "http://localhost:8083"
TOKEN = "Bearer test-token-123"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_session():
    """Re-create a fresh session before each test to avoid cross-test pollution."""
    import requests
    h.session = requests.Session()
    h.ELEMENT_CACHE.clear()
    yield
    h.session = requests.Session()
    h.ELEMENT_CACHE.clear()


# ---------------------------------------------------------------------------
# configure_session / get_session
# ---------------------------------------------------------------------------

class TestConfigureSession:
    def test_sets_authorization_header(self):
        configure_session(TOKEN)
        assert h.session.headers.get("Authorization") == TOKEN

    def test_sets_content_type_header(self):
        configure_session(TOKEN)
        assert h.session.headers.get("Content-Type") == "application/json"

    def test_stores_base_url(self):
        configure_session(TOKEN, BASE_URL)
        assert h.session.base_url == BASE_URL  # type: ignore[attr-defined]

    def test_returns_session_object(self):
        sess = configure_session(TOKEN)
        assert sess is h.session

    def test_get_session_returns_same_object(self):
        configure_session(TOKEN)
        assert get_session() is h.session

    def test_raises_on_empty_token(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            configure_session("")

    def test_raises_on_missing_bearer_prefix(self):
        with pytest.raises(ValueError, match="'Bearer '"):
            configure_session("my-raw-token")

    def test_accepts_mixed_case_bearer(self):
        # The validation is case-insensitive; normalization is left to the caller.
        configure_session("bearer my-token")  # should NOT raise


# ---------------------------------------------------------------------------
# get_projects — status-code handling
# ---------------------------------------------------------------------------

class TestGetProjects:
    def test_happy_path_returns_sorted_list(self):
        configure_session(TOKEN)
        projects = [
            {"name": "Zebra Project", "@id": "aaa"},
            {"name": "Alpha Project", "@id": "bbb"},
        ]
        with req_mock.Mocker(session=h.session) as m:
            m.get(f"{BASE_URL}/projects?page%5Bsize%5D=256", json=projects)
            result = h.get_projects(BASE_URL)
        assert result[0]["name"] == "Alpha Project"
        assert result[1]["name"] == "Zebra Project"

    def test_raises_auth_error_on_401(self):
        configure_session(TOKEN)
        with req_mock.Mocker(session=h.session) as m:
            m.get(f"{BASE_URL}/projects?page%5Bsize%5D=256", status_code=401, text="Unauthorized")
            with pytest.raises(SysMLV2AuthError):
                h.get_projects(BASE_URL)

    def test_raises_auth_error_on_403(self):
        configure_session(TOKEN)
        with req_mock.Mocker(session=h.session) as m:
            m.get(f"{BASE_URL}/projects?page%5Bsize%5D=256", status_code=403, text="Forbidden")
            with pytest.raises(SysMLV2AuthError):
                h.get_projects(BASE_URL)

    def test_raises_generic_api_error_on_500(self):
        configure_session(TOKEN)
        with req_mock.Mocker(session=h.session) as m:
            m.get(f"{BASE_URL}/projects?page%5Bsize%5D=256", status_code=500, text="Server Error")
            with pytest.raises(SysMLV2APIError) as exc_info:
                h.get_projects(BASE_URL)
            assert exc_info.value.status_code == 500

    def test_raises_not_found_on_404(self):
        configure_session(TOKEN)
        with req_mock.Mocker(session=h.session) as m:
            m.get(f"{BASE_URL}/projects?page%5Bsize%5D=256", status_code=404, text="Not found")
            with pytest.raises(SysMLV2NotFoundError):
                h.get_projects(BASE_URL)


# ---------------------------------------------------------------------------
# _check_response — exception hierarchy
# ---------------------------------------------------------------------------

class TestCheckResponse:
    """Unit-test _check_response directly."""

    def _fake_response(self, status_code: int, text: str = "error"):
        """Return a minimal fake Response object."""
        import requests
        r = requests.Response()
        r.status_code = status_code
        r._content = text.encode()
        return r

    def test_200_does_not_raise(self):
        import requests
        r = requests.Response()
        r.status_code = 200
        r._content = b"{}"
        h._check_response(r, "test")  # should not raise

    def test_204_does_not_raise(self):
        import requests
        r = requests.Response()
        r.status_code = 204
        r._content = b""
        h._check_response(r, "test")  # should not raise

    def test_401_raises_auth_error(self):
        import requests
        r = requests.Response()
        r.status_code = 401
        r._content = b"Unauthorized"
        with pytest.raises(SysMLV2AuthError):
            h._check_response(r)

    def test_409_raises_conflict_error(self):
        import requests
        r = requests.Response()
        r.status_code = 409
        r._content = b"Conflict"
        with pytest.raises(SysMLV2ConflictError):
            h._check_response(r)
