# Getting Started

## Installation

Install from PyPI:

```bash
pip install assured-py
```

Or with `uv`:

```bash
uv add assured-py
```

### Development Installation

To contribute or run tests locally:

```bash
git clone https://github.com/jhaisley/assured-py.git
cd assured-py
pip install -e ".[dev]"
```

## Configuration

The SDK reads configuration from environment variables, with automatic `.env` file discovery via `python-dotenv`.

### Required Environment Variables

Create a `.env` file in your project root:

```properties
ASSURED_BASE_URL=https://demo-backend.withassured.com
ASSURED_API_KEY=your-api-key-here
ASSURED_USER=your-email@example.com
ASSURED_PASS=your-password
```

| Variable | Required | Description |
|---|---|---|
| `ASSURED_BASE_URL` | Yes | Base URL of the Assured backend |
| `ASSURED_API_KEY` | Yes | API key sent via the `x-api-key` header |
| `ASSURED_USER` | For JWT endpoints | Email for programmatic login |
| `ASSURED_PASS` | For JWT endpoints | Password for programmatic login |

!!! note "When are credentials needed?"
    The API Key handles the vast majority of requests. However, certain undocumented endpoints — file uploading, SSN encryption, and document association — require user credentials (`ASSURED_USER` / `ASSURED_PASS`) to acquire an internal JWT session token. The client handles this transparently.

### `.env` File Discovery

The SDK uses `find_dotenv(usecwd=True)` to locate your `.env` file, starting from the **current working directory** of your script. It will log the path it found:

```
Loaded environment variables from: /path/to/your/project/.env
✅ Successfully found credentials for user@example.com
```

## Your First Request

```python
import asyncio
from assured import AssuredClient

async def main():
    async with AssuredClient() as client:
        # List all providers
        providers = await client.providers.list_all()
        for p in providers:
            print(f"{p.full_name} — NPI: {p.npi}")

asyncio.run(main())
```

### Using the Context Manager

`AssuredClient` is designed to be used as an async context manager, which ensures the underlying HTTP connection pool is properly cleaned up:

```python
async with AssuredClient() as client:
    # All your API calls here
    ...
# Connection pool is automatically closed
```

You can also manage the lifecycle manually:

```python
client = AssuredClient()
try:
    providers = await client.providers.list_all()
finally:
    await client.close()
```

## What's Next?

- **[Authentication Guide](guides/authentication.md)** — Understand the dual auth model
- **[Pagination Guide](guides/pagination.md)** — Master `list()`, `list_all()`, and `list_df()`
- **[File Uploads Guide](guides/file-uploads.md)** — Upload and associate documents
- **[API Reference](api/client.md)** — Full class and method documentation
