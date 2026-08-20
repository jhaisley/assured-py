"""Tests for the provider profile resource."""

from __future__ import annotations

import base64
import hashlib
import json

import httpx
import pytest
import respx

from assured.client import AssuredClient
from assured.models.provider_profile import (
    CDSRecordCreate,
    CertificationCreate,
    DEARecordCreate,
    EducationCreate,
    EmploymentCreate,
    LicenseCreate,
    MedicaidRecordCreate,
    MedicareRecordCreate,
    ProfessionalTrainingCreate,
    ProviderDocumentCreate,
    ProviderPersonalInfoUpdate,
)
from assured.settings import Settings
from tests.conftest import paginated_response

_BASE = "https://test-api.example.com"
_PERSONAL_INFO_URL = f"{_BASE}/api/v1/users/provider-personal-info/prof-1/"
_SSN_URL = f"{_BASE}/api/v1/users/retrieve-update-provider-ssn-sym-encrypted/prof-1/"
_EMPLOYMENT_URL = f"{_BASE}/api/v1/users/provider-employment-v1/"
_EDUCATION_URL = f"{_BASE}/api/v1/users/provider-education/"
_CERTS_URL = f"{_BASE}/api/v1/users/provider-certifications/"
_LICENSE_URL = f"{_BASE}/api/v1/users/provider-professional-ids-license/"
_DEA_URL = f"{_BASE}/api/v1/users/provider-professional-ids-dea/"
_CDS_URL = f"{_BASE}/api/v1/users/provider-professional-ids-cds/"
_MEDICAID_URL = f"{_BASE}/api/v1/users/provider-professional-ids-medicaid/"
_MEDICARE_URL = f"{_BASE}/api/v1/users/provider-professional-ids-medicare/"
_TRAINING_URL = f"{_BASE}/api/v1/users/provider-professional-training/"
_DOCUMENTS_URL = f"{_BASE}/api/v1/users/provider-documents/"


# ---- Personal Info ----


@pytest.mark.asyncio
async def test_get_personal_info(client, mock_api):
    mock_api.get(_PERSONAL_INFO_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "prof-1",
                "full_name": "Jane Q Doe",
                "first_name": "Jane",
                "last_name": "Doe",
                "gender": "Female",
                "birth_date": "1980-05-01",
                "height_inches": 66,
                "weight_in_lbs": 140,
                "hair_color": "BROWN",
                "eye_color": "HAZEL",
                "home_country": "USA",
                "public_email": "jane@public.example.com",
                "nucc_taxonomy_code": "207Q00000X",
                "management_type": "PROVIDER_MANAGED",
                "personal_completion_info": {"percentage": 90},
                "other_emails": ["alt@example.com"],
                "updated_at": "2026-08-01T12:00:00Z",
            },
        )
    )

    info = await client.provider_profile.get_personal_info("prof-1")
    assert info.id == "prof-1"
    assert info.full_name == "Jane Q Doe"
    assert info.height_inches == 66
    assert info.hair_color == "BROWN"
    assert info.management_type == "PROVIDER_MANAGED"
    assert info.personal_completion_info == {"percentage": 90}
    assert info.other_emails == ["alt@example.com"]
    assert info.updated_at is not None


@pytest.mark.asyncio
async def test_update_personal_info_fetch_merge(client, mock_api):
    mock_api.get(_PERSONAL_INFO_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "prof-1",
                "first_name": "Jane",
                "last_name": "Doe",
                "primary_email_address": "jane@example.com",
                "management_type": "PROVIDER_MANAGED",
                "updated_at": "2026-08-01T12:00:00Z",
                "personal_completion_info": {"percentage": 90},
            },
        )
    )
    patch_route = mock_api.patch(_PERSONAL_INFO_URL).mock(
        return_value=httpx.Response(200, json={"id": "prof-1", "first_name": "Janet", "last_name": "Doe"})
    )

    result = await client.provider_profile.update_personal_info(
        "prof-1",
        ProviderPersonalInfoUpdate(first_name="Janet"),
    )
    assert result.first_name == "Janet"

    payload = json.loads(patch_route.calls.last.request.read())
    # Overlaid change
    assert payload["first_name"] == "Janet"
    # Unmodified fields are merged in from the fetched record (full payload)
    assert payload["last_name"] == "Doe"
    assert payload["primary_email_address"] == "jane@example.com"
    # Nullable fields are sent as explicit nulls, not omitted
    assert "middle_name" in payload
    assert payload["middle_name"] is None
    # Response-only fields are stripped from the PATCH payload
    for read_only in ("id", "updated_at", "management_type", "personal_completion_info"):
        assert read_only not in payload


# ---- Encrypted SSN ----


@pytest.mark.asyncio
async def test_get_ssn(client, mock_api):
    route = mock_api.get(_SSN_URL).mock(
        return_value=httpx.Response(200, json={"id": "prof-1", "ssn": "b64-ciphertext"})
    )

    result = await client.provider_profile.get_ssn("prof-1", jwt="test-jwt")
    assert result == {"id": "prof-1", "ssn": "b64-ciphertext"}
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-jwt"


@pytest.mark.asyncio
async def test_update_ssn_encrypts_payload(client, mock_api):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    route = mock_api.patch(_SSN_URL).mock(return_value=httpx.Response(200, json={"id": "prof-1", "ssn": "ok"}))

    jwt = "test-jwt-token"
    result = await client.provider_profile.update_ssn("prof-1", ssn="123-45-6789", jwt=jwt)
    assert result["id"] == "prof-1"

    request = route.calls.last.request
    assert request.headers["Authorization"] == f"Bearer {jwt}"

    # Decrypt the payload and verify AES-256-CTR round trip (key = SHA256(jwt), IV prefixed)
    payload = json.loads(request.read())
    blob = base64.b64decode(payload["ssn"])
    iv, ciphertext = blob[:16], blob[16:]
    key = hashlib.sha256(jwt.encode("utf-8")).digest()
    decryptor = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend()).decryptor()
    assert decryptor.update(ciphertext) + decryptor.finalize() == b"123456789"


# ---- Employment (v1) ----


@pytest.mark.asyncio
async def test_list_employments(client, mock_api):
    mock_api.get(_EMPLOYMENT_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "emp-1",
                        "employer_name": "General Hospital",
                        "currently_employed": True,
                        "start_date": "2020-01-01",
                        "gap_explanation": "n/a",
                        "document": "s3://bucket/emp.pdf",
                        "provider": "prof-1",
                    },
                ]
            ),
        )
    )

    employments = await client.provider_profile.list_employments(provider="prof-1")
    assert len(employments) == 1
    assert employments[0].employer_name == "General Hospital"
    assert employments[0].currently_employed is True
    assert employments[0].document == "s3://bucket/emp.pdf"


@pytest.mark.asyncio
async def test_create_employment(client, mock_api):
    route = mock_api.post(_EMPLOYMENT_URL).mock(
        return_value=httpx.Response(201, json={"id": "emp-new", "employer_name": "Clinic"})
    )

    result = await client.provider_profile.create_employment(
        EmploymentCreate(
            provider="prof-1",
            employer_name="Clinic",
            currently_employed=False,
            reason_for_discontinuance="Relocated",
            document="s3://bucket/emp.pdf",
        )
    )
    assert result["id"] == "emp-new"

    payload = json.loads(route.calls.last.request.read())
    assert payload["currently_employed"] is False
    assert payload["reason_for_discontinuance"] == "Relocated"
    assert payload["document"] == "s3://bucket/emp.pdf"


# ---- Education ----


@pytest.mark.asyncio
async def test_create_education_with_document(client, mock_api):
    route = mock_api.post(_EDUCATION_URL).mock(
        return_value=httpx.Response(201, json={"id": "edu-1", "document": "s3://bucket/diploma.pdf"})
    )

    result = await client.provider_profile.create_education(
        EducationCreate(
            provider="prof-1",
            name="State University",
            degree="MD (Doctor of Medicine)",
            document="s3://bucket/diploma.pdf",
        )
    )
    assert result["id"] == "edu-1"

    payload = json.loads(route.calls.last.request.read())
    assert payload["document"] == "s3://bucket/diploma.pdf"
    assert payload["degree"] == "MD (Doctor of Medicine)"


# ---- Certifications ----


@pytest.mark.asyncio
async def test_create_certification_with_maintenance_of_certification(client, mock_api):
    route = mock_api.post(_CERTS_URL).mock(
        return_value=httpx.Response(201, json={"id": "cert-1", "maintenance_of_certification": True})
    )

    result = await client.provider_profile.create_certification(
        CertificationCreate(
            provider="prof-1",
            speciality="Family Medicine",
            speciality_level="PRIMARY",
            maintenance_of_certification=True,
        )
    )
    assert result["id"] == "cert-1"

    payload = json.loads(route.calls.last.request.read())
    assert payload["maintenance_of_certification"] is True
    assert payload["speciality_level"] == "PRIMARY"


# ---- Professional IDs ----


@pytest.mark.asyncio
async def test_create_license_with_document(client, mock_api):
    route = mock_api.post(_LICENSE_URL).mock(return_value=httpx.Response(201, json={"id": "lic-1"}))

    await client.provider_profile.create_license(
        LicenseCreate(provider="prof-1", state="CA", number="A12345", document="s3://bucket/license.pdf")
    )
    payload = json.loads(route.calls.last.request.read())
    assert payload["document"] == "s3://bucket/license.pdf"


@pytest.mark.asyncio
async def test_create_dea_with_new_fields(client, mock_api):
    route = mock_api.post(_DEA_URL).mock(return_value=httpx.Response(201, json={"id": "dea-1"}))

    await client.provider_profile.create_dea(
        DEARecordCreate(provider="prof-1", state="NY", number="BD1234567", is_available=True, document="s3://d.pdf")
    )
    payload = json.loads(route.calls.last.request.read())
    assert payload["is_available"] is True
    assert payload["document"] == "s3://d.pdf"


@pytest.mark.asyncio
async def test_create_cds_with_new_fields(client, mock_api):
    route = mock_api.post(_CDS_URL).mock(return_value=httpx.Response(201, json={"id": "cds-1"}))

    await client.provider_profile.create_cds(
        CDSRecordCreate(provider="prof-1", state="TX", license_unlimited=True, document="s3://c.pdf")
    )
    payload = json.loads(route.calls.last.request.read())
    assert payload["license_unlimited"] is True
    assert payload["document"] == "s3://c.pdf"


@pytest.mark.asyncio
async def test_create_medicaid_with_document(client, mock_api):
    route = mock_api.post(_MEDICAID_URL).mock(return_value=httpx.Response(201, json={"id": "mcd-1"}))

    await client.provider_profile.create_medicaid(
        MedicaidRecordCreate(provider="prof-1", state="WA", number="M-1", document="s3://m.pdf")
    )
    payload = json.loads(route.calls.last.request.read())
    assert payload["document"] == "s3://m.pdf"


@pytest.mark.asyncio
async def test_create_medicare_with_document(client, mock_api):
    route = mock_api.post(_MEDICARE_URL).mock(return_value=httpx.Response(201, json={"id": "mcr-1"}))

    await client.provider_profile.create_medicare(
        MedicareRecordCreate(provider="prof-1", state="WA", number="M-2", document="s3://m2.pdf")
    )
    payload = json.loads(route.calls.last.request.read())
    assert payload["document"] == "s3://m2.pdf"


# ---- Professional Training ----


@pytest.mark.asyncio
async def test_create_training_with_new_fields(client, mock_api):
    route = mock_api.post(_TRAINING_URL).mock(return_value=httpx.Response(201, json={"id": "tr-1"}))

    await client.provider_profile.create_training(
        ProfessionalTrainingCreate(
            provider="prof-1",
            institution_name="Teaching Hospital",
            training_type="Residency",
            speciality="Internal Medicine",
            is_program_successfully_completed=True,
            document="s3://bucket/training.pdf",
        )
    )
    payload = json.loads(route.calls.last.request.read())
    assert payload["training_type"] == "Residency"
    assert payload["speciality"] == "Internal Medicine"
    assert payload["is_program_successfully_completed"] is True
    assert payload["document"] == "s3://bucket/training.pdf"


# ---- Documents ----


@pytest.mark.asyncio
async def test_list_documents(client, mock_api):
    client._jwt_cache = "mock-jwt"  # skip the lazy login (endpoint is JWT-only in production)
    mock_api.get(_DOCUMENTS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "doc-1",
                        "provider": "prof-1",
                        "document_name": "License scan",
                        "document_type": "STATE_LICENSE",
                        "document_url": "s3://bucket/lic.pdf",
                        "file_checksum": "abc123",
                        "uploaded_date": "2026-08-01",
                        "expiration_date": "2027-08-01",
                        "state": "CA",
                    },
                ]
            ),
        )
    )

    docs = await client.provider_profile.list_documents(provider="prof-1")
    assert len(docs) == 1
    assert docs[0].id == "doc-1"
    assert docs[0].file_checksum == "abc123"
    assert docs[0].state == "CA"


@pytest.mark.asyncio
async def test_list_documents_df(client, mock_api):
    client._jwt_cache = "mock-jwt"  # skip the lazy login (endpoint is JWT-only in production)
    mock_api.get(_DOCUMENTS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "doc-1", "provider": "prof-1", "document_name": "W-9", "document_type": "TAX_FORM"},
                ]
            ),
        )
    )

    df = await client.provider_profile.list_documents_df(provider="prof-1")
    assert "document_name" in df.columns
    assert len(df) == 1


@pytest.mark.asyncio
async def test_create_document_requires_jwt():
    settings = Settings(
        base_url="https://api.assured.test",
        api_key="test-api-key",
        user="dev@test.com",
        **{"assured_pass": "password123"},
    )
    async with AssuredClient(settings=settings) as client:
        with respx.mock(assert_all_called=True) as mocker:
            mocker.post("https://api.assured.test/api/v1/users/login/").mock(
                return_value=httpx.Response(200, json={"data": {"jwt": {"access": "mock-jwt"}}})
            )
            route = mocker.post("https://api.assured.test/api/v1/users/provider-documents/").mock(
                return_value=httpx.Response(
                    201,
                    json={
                        "id": "doc-new",
                        "provider": "prof-1",
                        "document_name": "License scan",
                        "file_checksum": "abc123",
                        "state": "CA",
                    },
                )
            )

            doc = await client.provider_profile.create_document(
                ProviderDocumentCreate(
                    provider="prof-1",
                    document_name="License scan",
                    document_type="STATE_LICENSE",
                    document_url="s3://bucket/lic.pdf",
                    file_checksum="abc123",
                    state="CA",
                )
            )
            assert doc.id == "doc-new"
            assert doc.file_checksum == "abc123"

            request = route.calls.last.request
            assert request.headers["Authorization"] == "Bearer mock-jwt"
            payload = json.loads(request.read())
            assert payload["file_checksum"] == "abc123"
            assert payload["state"] == "CA"


@pytest.mark.asyncio
async def test_upload_and_associate_document():
    settings = Settings(
        base_url="https://api.assured.test",
        api_key="test-api-key",
        user="dev@test.com",
        **{"assured_pass": "password123"},
    )
    async with AssuredClient(settings=settings) as client:
        with respx.mock(assert_all_called=True) as mocker:
            mocker.post("https://api.assured.test/api/v1/users/login/").mock(
                return_value=httpx.Response(200, json={"data": {"jwt": {"access": "mock-jwt"}}})
            )
            mocker.post("https://api.assured.test/api/v1/files/handle/").mock(
                return_value=httpx.Response(
                    201,
                    json={"id": "file-1", "file_url": "s3://assured-bots/mock.pdf", "name": "random.pdf"},
                )
            )
            doc_route = mocker.post("https://api.assured.test/api/v1/users/provider-documents/").mock(
                return_value=httpx.Response(
                    201,
                    json={"id": "doc-1", "provider": "prof-1", "document_url": "s3://assured-bots/mock.pdf"},
                )
            )

            doc = await client.provider_profile.upload_and_associate_document(
                provider_id="prof-1",
                file_content=b"fake-pdf-content",
                filename="mock.pdf",
                document_name="License scan",
                document_type="STATE_LICENSE",
            )
            assert doc.id == "doc-1"
            assert doc.document_url == "s3://assured-bots/mock.pdf"

            payload = json.loads(doc_route.calls.last.request.read())
            assert payload["provider"] == "prof-1"
            assert payload["document_url"] == "s3://assured-bots/mock.pdf"
