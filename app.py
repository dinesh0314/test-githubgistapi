from fastapi import FastAPI, HTTPException, Query
import httpx

app = FastAPI(title="GitHub Gists API", description="Returns public gists for a GitHub user")

GITHUB_API_BASE = "https://api.github.com"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/{username}")
async def get_user_gists(
    username: str,
    page: int = Query(default=1, ge=1, description="Page number (default: 1)"),
    per_page: int = Query(default=30, ge=1, le=100, description="Results per page (max: 100)"),
):
    """Return a list of public gists for the given GitHub username."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/users/{username}/gists",
            params={"page": page, "per_page": per_page},
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "github-gists-api",
            },
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error: status {response.status_code}",
        )

    return [
        {
            "id": gist["id"],
            "description": gist["description"],
            "public": gist["public"],
            "html_url": gist["html_url"],
            "files": list(gist["files"].keys()),
            "created_at": gist["created_at"],
            "updated_at": gist["updated_at"],
        }
        for gist in response.json()
    ]
