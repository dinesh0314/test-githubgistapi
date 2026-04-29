# GitHub Gists API

A simple HTTP web server that returns a list of public Gists for a given GitHub username.

---

## Prerequisites

- Python 3.12+
- Docker (for containerised run)

---

## Local Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8080
```

API is available at `http://localhost:8080/<github-username>`

---

## Run Tests

```bash
# With venv activated
pytest test_app.py -v
```

---

## Docker Setup

```bash
# Build the image
docker build -t gists-api .

# Run the container
docker run -d -p 8080:8080 --name gists-api gists-api

# Test the endpoint
curl http://localhost:8080/octocat

# Stop and remove
docker stop gists-api && docker rm gists-api
```

---

## API Usage

| Endpoint | Description |
|---|---|
| `GET /<username>` | Returns public gists for the given GitHub user |
| `GET /<username>?page=2&per_page=10` | Paginated results (max `per_page`: 100) |

**Example:**
```bash
curl http://localhost:8080/octocat
```

**Response:**
```json
[
  {
    "id": "abc123",
    "description": "Hello World",
    "public": true,
    "html_url": "https://gist.github.com/octocat/abc123",
    "files": ["hello_world.py"],
    "created_at": "2021-01-01T00:00:00Z",
    "updated_at": "2021-06-15T12:00:00Z"
  }
]
```
