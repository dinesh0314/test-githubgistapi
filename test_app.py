import httpx
import respx
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

MOCK_GISTS = [
    {
        "id": "abc123",
        "description": "Hello World",
        "public": True,
        "html_url": "https://gist.github.com/octocat/abc123",
        "files": {
            "hello_world.py": {
                "filename": "hello_world.py",
                "type": "application/x-python",
            }
        },
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-06-15T12:00:00Z",
    },
    {
        "id": "def456",
        "description": "Octocat test gist",
        "public": True,
        "html_url": "https://gist.github.com/octocat/def456",
        "files": {
            "test.md": {
                "filename": "test.md",
                "type": "text/markdown",
            }
        },
        "created_at": "2022-03-10T08:30:00Z",
        "updated_at": "2022-03-10T08:30:00Z",
    },
]

GITHUB_GISTS_URL = "https://api.github.com/users/octocat/gists"


@respx.mock
def test_get_octocat_gists_success():
    """Test that a valid user returns their gists with the expected structure."""
    respx.get(GITHUB_GISTS_URL).mock(return_value=httpx.Response(200, json=MOCK_GISTS))

    response = client.get("/octocat")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    first = data[0]
    assert first["id"] == "abc123"
    assert first["description"] == "Hello World"
    assert first["public"] is True
    assert first["html_url"] == "https://gist.github.com/octocat/abc123"
    assert "hello_world.py" in first["files"]
    assert "created_at" in first
    assert "updated_at" in first


@respx.mock
def test_user_not_found():
    """Test that a non-existent user returns 404."""
    respx.get("https://api.github.com/users/this-user-does-not-exist-xyz/gists").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )

    response = client.get("/this-user-does-not-exist-xyz")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@respx.mock
def test_github_api_error_returns_502():
    """Test that a GitHub API failure surfaces as 502 Bad Gateway."""
    respx.get(GITHUB_GISTS_URL).mock(
        return_value=httpx.Response(503, json={"message": "Service Unavailable"})
    )

    response = client.get("/octocat")

    assert response.status_code == 502
    assert "GitHub API error" in response.json()["detail"]


@respx.mock
def test_empty_gist_list():
    """Test that a user with no gists returns an empty list."""
    respx.get("https://api.github.com/users/nogists/gists").mock(
        return_value=httpx.Response(200, json=[])
    )

    response = client.get("/nogists")

    assert response.status_code == 200
    assert response.json() == []


@respx.mock
def test_pagination_params_accepted():
    """Test that page/per_page query params are accepted and forwarded."""
    respx.get(GITHUB_GISTS_URL).mock(return_value=httpx.Response(200, json=MOCK_GISTS))

    response = client.get("/octocat?page=2&per_page=10")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@respx.mock
def test_response_fields_shape():
    """Test that every gist in the response has all required fields."""
    respx.get(GITHUB_GISTS_URL).mock(return_value=httpx.Response(200, json=MOCK_GISTS))

    data = client.get("/octocat").json()

    required_keys = {"id", "description", "public", "html_url", "files", "created_at", "updated_at"}
    for gist in data:
        assert required_keys == set(gist.keys())
        assert isinstance(gist["files"], list)