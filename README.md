# Assured Platform API — Unofficial Python SDK

An unofficial, modern, async-first Python SDK wrapping the **Assured Platform API**. This library provides fully typed Pydantic models, automatic semantic pagination, and robust file handling designed to streamline interactions with Assured's complex backend.

[![CI](https://github.com/jhaisley/assured-py/actions/workflows/ci.yml/badge.svg)](https://github.com/jhaisley/assured-py/actions/workflows/ci.yml)
[![CodeQL Advanced](https://github.com/jhaisley/assured-py/actions/workflows/codeql.yml/badge.svg)](https://github.com/jhaisley/assured-py/actions/workflows/codeql.yml)
[![GitHub release](https://img.shields.io/github/release/Naereen/StrapDown.js.svg)](https://GitHub.com/Naereen/StrapDown.js/releases/)
[![PyPI version fury.io](https://badge.fury.io/py/assured-py.svg)](https://pypi.python.org/pypi/assured-py/)
[![Docs](https://readthedocs.org/projects/assured-py/badge/?version=latest)](https://assured-py.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) ![uv](https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white)

[![Open Demo In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jnhaisley/assured-py/assured_py_demo.ipynb)

## Features

- **Async First**: Built on `httpx` to support highly concurrent workflows seamlessly.
- **Type Safety**: Thoroughly documented Pydantic v2 classes represent the massive web of API payloads.
- **Auto-Pagination**: Helper methods to pull data incrementally or extract directly into `pandas.DataFrames`.
- **Session Bridge**: A custom JWT authentication layer to shim missing capabilities for undocumented storage and encryption endpoints.

## Setup & Installation

The package manages dependencies using standard Python environments (`uv`, `hatch`, or `pip`). The primary configuration is driven via environment variables.

### Prerequisites

Create a `.env` file in your root directory based on the `.env.example`:

```properties
ASSURED_BASE_URL=https://demo-backend.withassured.com
ASSURED_API_KEY=your-api-key-here
ASSURED_USER=your-email@example.com
ASSURED_PASS=your-password
```

> [!NOTE]
> The API Key handles 95% of requests. However, certain undocumented endpoints like file uploading and SSN encryption require explicit user credentials (`ASSURED_USER` and `ASSURED_PASS`) to acquire an internal JWT session token. The client handles fetching and caching this JWT automatically.

## Quickstart

```python
import asyncio
from assured import AssuredClient

async def run():
    # Automatically loads configuration from your `.env` file using pydantic-settings
    async with AssuredClient() as client:
        
        # 1. Standard API Key usage: List all providers into a DataFrame
        providers_df = await client.providers.list_df()
        print(providers_df[["full_name", "npi", "email"]])

        # 2. Extract provider details
        detail = await client.credentialing.get_request("some-uuid")
        provider_profile_id = detail.provider_id
        
        # 3. Use undocumented JWT bridging: Upload and associate a document seamlessly!
        # The client recognizes this requires a JWT, fetches one leveraging your User credentials, 
        # posts the multipart payload to S3, and links it into the provider profile.
        contract_bytes = b"..."
        document = await client.provider_profile.upload_and_associate_document(
            provider_id=provider_profile_id,
            file_content=contract_bytes,
            filename="contract.pdf",
            document_name="IHCP Rendering Provider Agreement",
            document_type="Individual Provider Agreement",
        )
        
        # 4. Generate short-lived presigned URLs for assets
        secure_link = await client.files.presign_url(document.document_url)
        print(f"Download the document at: {secure_link}")

if __name__ == "__main__":
    asyncio.run(run())
```

## Structure & Architecture

The domains mirror Assured's core logical groupings:

- `client.users`: Managing internal roles.
- `client.providers`: Listing, fetching context, and inviting user providers.
- `client.provider_profile`: Encompasses deep profiles ranging from demographics to DEAs to Gap Histories.
- `client.credentialing`: Operations wrapping verification tasks.
- `client.files`: Storage abstraction logic.

## Known Discrepancies

The Assured API contains numerous behaviors that diverge from documented OpenAPI specs. To see the specific differences this SDK automatically handles under-the-hood (like Encrypted SSNs and S3 Bucket paths), check out the [API Divergence Document](API_Divergence.md).
