# File Uploads & Document Association

Uploading files to the Assured Platform is a **two-stage process** that the SDK abstracts into a single method call.

## The Two-Stage Process

Under the hood, associating a file with a provider requires:

1. **Upload to S3** — POST the binary file to `/api/v1/files/handle/` (JWT-protected), which returns an internal `s3://` URI.
2. **Associate with Provider** — POST the S3 URI along with metadata to `/api/v1/users/provider-documents/` (also JWT-protected).

The SDK's `upload_and_associate_document()` handles both steps seamlessly.

## Supported File Formats

The Assured upload endpoint only accepts the following formats:

| Format | Extensions |
|---|---|
| PDF | `.pdf` |
| PNG | `.png` |
| JPEG | `.jpg`, `.jpeg` |

!!! warning "Format Validation"
    The SDK validates file extensions **before** making any network requests. Attempting to upload an unsupported format raises a `ValueError` immediately.

## Quick Upload

```python
async with AssuredClient() as client:
    with open("license.pdf", "rb") as f:
        document = await client.provider_profile.upload_and_associate_document(
            provider_id="profile-uuid-here",
            file_content=f.read(),
            filename="license.pdf",
            document_name="State Medical License",
            document_type="License",
        )

    print(f"Document ID: {document.id}")
    print(f"Storage URL: {document.document_url}")
```

## Generating Presigned URLs

Files stored in S3 are not publicly accessible. To generate a temporary download link:

```python
presigned_url = await client.files.presign_url(document.document_url)
print(f"Download at: {presigned_url}")
```

!!! note
    Presigned URLs are short-lived. Generate them on-demand rather than caching them.

## Low-Level Upload

If you need more control, you can use the file resource directly:

```python
# Step 1: Upload raw file
file_record = await client.files.upload(
    file_content=raw_bytes,
    filename="scan.png",
    mime_type="image/png",
)

# Step 2: Associate manually
from assured.models.provider_profile import ProviderDocumentCreate

doc = ProviderDocumentCreate(
    provider="provider-profile-uuid",
    document_name="Background Check",
    document_type="Verification",
    document_url=file_record.file_url,
)
result = await client.provider_profile.create_document(doc)
```

## Error Handling

```python
from assured.exceptions import AssuredAPIError

try:
    doc = await client.provider_profile.upload_and_associate_document(
        provider_id="...",
        file_content=content,
        filename="report.docx",  # Unsupported format!
        document_name="Report",
        document_type="Other",
    )
except ValueError as e:
    print(f"Validation error: {e}")
    # "Unsupported file format: '.docx'. Assured only accepts PDF, PNG, and JPEG files."

except AssuredAPIError as e:
    print(f"API error {e.status_code}: {e.detail}")
```
