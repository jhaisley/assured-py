# assured-py

**Unofficial Python SDK for the Assured Platform API**

[![CI](https://github.com/jhaisley/assured-py/actions/workflows/ci.yml/badge.svg)](https://github.com/jhaisley/assured-py/actions/workflows/ci.yml)
[![CodeQL](https://github.com/jhaisley/assured-py/actions/workflows/codeql.yml/badge.svg)](https://github.com/jhaisley/assured-py/actions/workflows/codeql.yml)
[![PyPI](https://img.shields.io/pypi/v/assured-py.svg)](https://pypi.org/project/assured-py/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

A modern, async-first Python SDK wrapping the **Assured Platform API**. Built with fully typed Pydantic v2 models, automatic semantic pagination, and robust file handling designed to streamline interactions with Assured's complex backend.

## Why assured-py?

The Assured Platform API has extensive undocumented behaviors, silent endpoint migrations, and multi-stage workflows that aren't obvious from the OpenAPI spec alone. This SDK was built to **bridge those gaps** — handling encrypted SSNs, JWT session management, S3 file orchestration, and more, so you don't have to.

## Key Features

- :zap: **Async First** — Built on `httpx` for highly concurrent workflows
- :shield: **Type Safety** — Pydantic v2 models for every request and response
- :page_facing_up: **Auto-Pagination** — Pull all records or export directly to `pandas.DataFrame`
- :key: **Session Bridge** — Transparent JWT caching for undocumented endpoints
- :file_folder: **File Orchestration** — Single-call upload + associate for provider documents
- :lock: **SSN Encryption** — AES-256-CTR encryption matching the platform's frontend scheme

## Quick Example

```python
import asyncio
from assured import AssuredClient

async def main():
    async with AssuredClient() as client:
        # List all providers as a DataFrame
        df = await client.providers.list_df()
        print(df[["full_name", "npi", "email"]])

        # Upload and associate a document in one call
        with open("contract.pdf", "rb") as f:
            doc = await client.provider_profile.upload_and_associate_document(
                provider_id="...",
                file_content=f.read(),
                filename="contract.pdf",
                document_name="Provider Agreement",
                document_type="Individual Provider Agreement",
            )

asyncio.run(main())
```

## Resources at a Glance

| Resource | Access | Description |
|---|---|---|
| **Users** | `client.users` | User management, login, password resets |
| **Providers** | `client.providers` | List, search, invite, NPI lookup |
| **Provider Profile** | `client.provider_profile` | Demographics, licenses, DEA, certifications, documents |
| **Credentialing** | `client.credentialing` | Verification requests and tasks |
| **Payer Enrollment** | `client.payer_enrollment` | Health plans, enrollment requests, active enrollments |
| **Files** | `client.files` | S3 uploads and presigned URL generation |

---

Get started with the [installation guide](getting-started.md), or dive into the [API reference](api/client.md).
