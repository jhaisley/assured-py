"""Provider profile resource (certifications, licenses, IDs, etc.)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.provider_profile import (
    CDSRecord,
    CDSRecordCreate,
    Certification,
    CertificationCreate,
    DEARecord,
    DEARecordCreate,
    Education,
    EducationCreate,
    Employment,
    EmploymentCreate,
    GapHistory,
    GapHistoryCreate,
    License,
    LicenseCreate,
    MedicaidRecord,
    MedicaidRecordCreate,
    MedicareRecord,
    MedicareRecordCreate,
    ProfessionalLiabilityInsurance,
    ProfessionalLiabilityInsuranceCreate,
    ProfessionalTraining,
    ProfessionalTrainingCreate,
    ProviderDocument,
    ProviderDocumentCreate,
    ProviderPersonalInfo,
    ProviderPersonalInfoUpdate,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

# API path constants
_CERTS = "/api/v1/users/provider-certifications/"
_LICENSE = "/api/v1/users/provider-professional-ids-license/"
_DEA = "/api/v1/users/provider-professional-ids-dea/"
_CDS = "/api/v1/users/provider-professional-ids-cds/"
_MEDICAID = "/api/v1/users/provider-professional-ids-medicaid/"
_MEDICARE = "/api/v1/users/provider-professional-ids-medicare/"
_EMPLOYMENT = "/api/v1/users/provider-employment-v1/"
_GAP = "/api/v1/users/provider-gap-history/"
_EDUCATION = "/api/v1/users/provider-education/"
_TRAINING = "/api/v1/users/provider-professional-training/"
_DOCUMENTS = "/api/v1/users/provider-documents/"
_INSURANCE = "/api/v1/users/provider-professional-liability-insurances/"
_PERSONAL_INFO = "/api/v1/users/provider-personal-info/{id}/"
_SSN = "/api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{id}/"

# Response-only personal-info fields that the documented PATCH schema does not
# accept; they are stripped from the fetch-merge-patch payload.
_PERSONAL_INFO_READ_ONLY = frozenset(
    {
        "id",
        "last_caqh_attestation_date",
        "other_emails",
        "other_names",
        "personal_completion_info",
        "management_type",
        "updated_at",
        # ssn is response-only here too: production returns a masked/ciphertext
        # value on GET, which must never be echoed back. SSN updates go through
        # the dedicated encrypted endpoint (update_ssn). An explicitly set ssn
        # on the update payload is still honored, as user fields are overlaid
        # after this strip.
        "ssn",
    }
)


def _params(
    provider: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    **extra: Any,
) -> dict[str, Any]:
    p: dict[str, Any] = {}
    if provider is not None:
        p["provider"] = provider
    if limit is not None:
        p["limit"] = limit
    if offset is not None:
        p["offset"] = offset
    p.update(extra)
    return p


class ProviderProfileResource:
    """Operations on provider profile data (certs, licenses, IDs, etc.)."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    # ---- Personal Info ----

    async def get_personal_info(self, provider_id: str) -> ProviderPersonalInfo:
        """GET provider personal info by provider profile ID.

        Backed by ``GET /api/v1/users/provider-personal-info/{id}/``, which is
        now officially documented (previously reverse-engineered).
        """
        path = _PERSONAL_INFO.format(id=provider_id)
        data = await self._client._get(path)
        return ProviderPersonalInfo.model_validate(data)

    async def update_personal_info(
        self,
        provider_id: str,
        data: ProviderPersonalInfoUpdate,
    ) -> ProviderPersonalInfo:
        """PATCH provider personal info (partial update).

        Backed by ``PATCH /api/v1/users/provider-personal-info/{id}/``, which
        is now officially documented (previously reverse-engineered). This
        method fetches the current record, overlays your changes and re-sends
        the populated fields, so you only need to set what you want to change.

        Null-valued fields are *not* re-sent. Most fields are non-nullable on
        the way in, so echoing back a null the GET returned draws HTTP 400
        ("This field may not be null."). This matters most right after
        ``providers.create()``, when the profile is almost entirely null.

        Note:
            Regardless of what you are setting, this endpoint rejects any
            PATCH that leaves citizenship unset ("Citizenship country is
            required", "Visa number is required for non-US citizens"). Send
            ``us_citizen`` and ``citizenship_country`` on the first write to a
            new profile.

        Response-only fields (``id``, ``updated_at``, ``management_type``,
        ``personal_completion_info``, ``other_emails``, ``other_names``,
        ``last_caqh_attestation_date``, ``ssn``) are stripped from the merged
        payload, as the documented PATCH request schema does not accept them.
        The fetched ``ssn`` in particular is masked/ciphertext in production
        and must not be echoed back — use :meth:`update_ssn` to change an SSN.
        A value you explicitly set on ``data`` is still sent.
        """
        # 1. Fetch current state as JSON-safe dict (all fields, dates as ISO strings)
        current = await self.get_personal_info(provider_id)
        merged = current.model_dump(mode="json")

        # 2. Strip response-only fields the PATCH schema does not accept
        for key in _PERSONAL_INFO_READ_ONLY:
            merged.pop(key, None)

        # 3. Drop fetched nulls. Most fields are non-nullable on the way in, so
        # echoing back a null the GET handed us is rejected with HTTP 400
        # ("This field may not be null."). An unpopulated profile -- e.g. one
        # just created via create-providers -- is almost entirely null, so
        # without this the first PATCH after a create always fails.
        merged = {k: v for k, v in merged.items() if v is not None}

        # 4. Overlay user-provided fields (explicit None → sends null to clear)
        merged.update(data.model_dump(mode="json", exclude_unset=True))

        # 5. PATCH
        path = _PERSONAL_INFO.format(id=provider_id)
        resp = await self._client._patch(path, json=merged)
        return ProviderPersonalInfo.model_validate(resp)

    async def get_ssn(self, provider_id: str, jwt: str) -> dict[str, Any]:
        """Retrieve a provider's SSN record from the encrypted-SSN endpoint.

        Backed by ``GET /api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{id}/``,
        now officially documented. The spec describes the payload as a plain
        ``{"id": ..., "ssn": ...}``; in production the ``ssn`` value is a
        symmetrically encrypted token, and the endpoint requires JWT Bearer
        auth instead of the standard API key.

        Args:
            provider_id: The provider *profile* ID.
            jwt: A valid session JWT (see ``client.users.login``).

        Returns:
            The raw response dict (``ssn`` is ciphertext, not plaintext).
        """
        path = _SSN.format(id=provider_id)
        url = self._client.settings.base_url.rstrip("/") + path

        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={"Authorization": f"Bearer {jwt}"},
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()

    async def update_ssn(self, provider_id: str, ssn: str, jwt: str) -> dict[str, Any]:
        """Encrypt and update a provider's SSN.

        Backed by ``PATCH /api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{id}/``,
        which is now officially documented — but the spec describes the payload
        as a plain ``{"ssn": "string"}`` and says nothing about encryption. In
        production the SSN must be symmetrically encrypted using AES-256-CTR
        with a key derived from the SHA-256 hash of the session JWT, with a
        random 16-byte IV prefixed to the ciphertext before Base64 encoding.
        This endpoint also requires the JWT for Bearer auth instead of the
        standard API key. The SDK keeps the production behavior.

        Note:
            Production also exposes a *plaintext* SSN endpoint,
            ``/api/v1/users/retrieve-update-provider-ssn/{id}/``, which is
            absent from the bundled spec. It is **read-only** — its documented
            ``PATCH`` answers ``400 "SSN is not updatable via this endpoint."``
            — so this encrypted write is still the only way to set an SSN.

            Use the plaintext endpoint to verify a write: ``GET`` it after
            calling this method and it returns the decrypted value, confirming
            the server accepted the ciphertext correctly. Reading back through
            this endpoint only returns ciphertext. See API_Divergence.md
            sections 5 and 12.
        """
        import base64
        import hashlib
        import os

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        # Normalize SSN
        ssn_digits = ssn.replace("-", "").strip()

        # Encrypt SSN using Assured's frontend scheme
        key = hashlib.sha256(jwt.encode("utf-8")).digest()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        enc = cipher.encryptor()
        ciphertext = enc.update(ssn_digits.encode("utf-8")) + enc.finalize()
        encrypted_ssn = base64.b64encode(iv + ciphertext).decode("ascii")

        # Execute PATCH Request with Bearer Auth
        path = _SSN.format(id=provider_id)
        url = self._client.settings.base_url.rstrip("/") + path

        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                url,
                json={"ssn": encrypted_ssn},
                headers={"Authorization": f"Bearer {jwt}"},
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()

    # ---- Certifications ----

    async def list_certifications(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Certification]:
        data = await self._client._get_page(_CERTS, params=_params(provider, limit, offset))
        return [Certification.model_validate(i) for i in data.get("results", [])]

    async def list_certifications_all(self, *, provider: str | None = None) -> list[Certification]:
        records = await self._client._get_all_pages(_CERTS, params=_params(provider))
        return [Certification.model_validate(i) for i in records]

    async def list_certifications_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_CERTS, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_certification(self, data: CertificationCreate) -> dict[str, Any]:
        return await self._client._post(_CERTS, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Licenses ----

    async def list_licenses(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[License]:
        data = await self._client._get_page(_LICENSE, params=_params(provider, limit, offset))
        return [License.model_validate(i) for i in data.get("results", [])]

    async def list_licenses_all(self, *, provider: str | None = None) -> list[License]:
        records = await self._client._get_all_pages(_LICENSE, params=_params(provider))
        return [License.model_validate(i) for i in records]

    async def list_licenses_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_LICENSE, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_license(self, data: LicenseCreate) -> dict[str, Any]:
        return await self._client._post(_LICENSE, json=data.model_dump(mode="json", exclude_none=False))

    # ---- DEA ----

    async def list_dea(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[DEARecord]:
        data = await self._client._get_page(_DEA, params=_params(provider, limit, offset))
        return [DEARecord.model_validate(i) for i in data.get("results", [])]

    async def list_dea_all(self, *, provider: str | None = None) -> list[DEARecord]:
        records = await self._client._get_all_pages(_DEA, params=_params(provider))
        return [DEARecord.model_validate(i) for i in records]

    async def list_dea_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_DEA, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_dea(self, data: DEARecordCreate) -> dict[str, Any]:
        return await self._client._post(_DEA, json=data.model_dump(mode="json", exclude_none=False))

    # ---- CDS ----

    async def list_cds(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[CDSRecord]:
        data = await self._client._get_page(_CDS, params=_params(provider, limit, offset))
        return [CDSRecord.model_validate(i) for i in data.get("results", [])]

    async def list_cds_all(self, *, provider: str | None = None) -> list[CDSRecord]:
        records = await self._client._get_all_pages(_CDS, params=_params(provider))
        return [CDSRecord.model_validate(i) for i in records]

    async def list_cds_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_CDS, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_cds(self, data: CDSRecordCreate) -> dict[str, Any]:
        return await self._client._post(_CDS, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Medicaid ----

    async def list_medicaid(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[MedicaidRecord]:
        data = await self._client._get_page(_MEDICAID, params=_params(provider, limit, offset))
        return [MedicaidRecord.model_validate(i) for i in data.get("results", [])]

    async def list_medicaid_all(self, *, provider: str | None = None) -> list[MedicaidRecord]:
        records = await self._client._get_all_pages(_MEDICAID, params=_params(provider))
        return [MedicaidRecord.model_validate(i) for i in records]

    async def list_medicaid_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_MEDICAID, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_medicaid(self, data: MedicaidRecordCreate) -> dict[str, Any]:
        return await self._client._post(_MEDICAID, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Medicare ----

    async def list_medicare(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[MedicareRecord]:
        data = await self._client._get_page(_MEDICARE, params=_params(provider, limit, offset))
        return [MedicareRecord.model_validate(i) for i in data.get("results", [])]

    async def list_medicare_all(self, *, provider: str | None = None) -> list[MedicareRecord]:
        records = await self._client._get_all_pages(_MEDICARE, params=_params(provider))
        return [MedicareRecord.model_validate(i) for i in records]

    async def list_medicare_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_MEDICARE, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_medicare(self, data: MedicareRecordCreate) -> dict[str, Any]:
        return await self._client._post(_MEDICARE, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Employment ----

    async def list_employments(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Employment]:
        """List provider employment records (one page).

        Backed by ``GET /api/v1/users/provider-employment-v1/``, which is now
        officially documented. The legacy ``/provider-employments/`` endpoint
        has been removed from the spec; the SDK already targets v1.
        """
        data = await self._client._get_page(_EMPLOYMENT, params=_params(provider, limit, offset))
        return [Employment.model_validate(i) for i in data.get("results", [])]

    async def list_employments_all(self, *, provider: str | None = None) -> list[Employment]:
        records = await self._client._get_all_pages(_EMPLOYMENT, params=_params(provider))
        return [Employment.model_validate(i) for i in records]

    async def list_employments_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_EMPLOYMENT, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_employment(self, data: EmploymentCreate) -> dict[str, Any]:
        """Create an employment record via ``POST /api/v1/users/provider-employment-v1/`` (now documented)."""
        return await self._client._post(_EMPLOYMENT, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Gap History ----

    async def list_gap_history(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[GapHistory]:
        data = await self._client._get_page(_GAP, params=_params(provider, limit, offset))
        return [GapHistory.model_validate(i) for i in data.get("results", [])]

    async def list_gap_history_all(self, *, provider: str | None = None) -> list[GapHistory]:
        records = await self._client._get_all_pages(_GAP, params=_params(provider))
        return [GapHistory.model_validate(i) for i in records]

    async def list_gap_history_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_GAP, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_gap_history(self, data: GapHistoryCreate) -> dict[str, Any]:
        return await self._client._post(_GAP, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Education ----

    async def list_education(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Education]:
        data = await self._client._get_page(_EDUCATION, params=_params(provider, limit, offset))
        return [Education.model_validate(i) for i in data.get("results", [])]

    async def list_education_all(self, *, provider: str | None = None) -> list[Education]:
        records = await self._client._get_all_pages(_EDUCATION, params=_params(provider))
        return [Education.model_validate(i) for i in records]

    async def list_education_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_EDUCATION, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_education(self, data: EducationCreate) -> dict[str, Any]:
        return await self._client._post(_EDUCATION, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Professional Training ----

    async def list_training(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProfessionalTraining]:
        data = await self._client._get_page(_TRAINING, params=_params(provider, limit, offset))
        return [ProfessionalTraining.model_validate(i) for i in data.get("results", [])]

    async def list_training_all(self, *, provider: str | None = None) -> list[ProfessionalTraining]:
        records = await self._client._get_all_pages(_TRAINING, params=_params(provider))
        return [ProfessionalTraining.model_validate(i) for i in records]

    async def list_training_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_TRAINING, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_training(self, data: ProfessionalTrainingCreate) -> dict[str, Any]:
        return await self._client._post(_TRAINING, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Documents ----

    async def list_documents(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProviderDocument]:
        """List provider documents (one page).

        Backed by ``GET /api/v1/users/provider-documents/`` (new in the spec).
        Production enforces JWT Bearer auth on this endpoint despite the spec's
        API-key security claim, so the SDK bridges to a session JWT automatically.
        """
        data = await self._client._get_page(_DOCUMENTS, params=_params(provider, limit, offset), requires_jwt=True)
        return [ProviderDocument.model_validate(i) for i in data.get("results", [])]

    async def list_documents_all(self, *, provider: str | None = None) -> list[ProviderDocument]:
        """List all provider documents across every page."""
        records = await self._client._get_all_pages(_DOCUMENTS, params=_params(provider), requires_jwt=True)
        return [ProviderDocument.model_validate(i) for i in records]

    async def list_documents_df(self, *, provider: str | None = None) -> pd.DataFrame:
        """List all provider documents as a pandas DataFrame."""
        records = await self._client._get_all_pages(_DOCUMENTS, params=_params(provider), requires_jwt=True)
        return self._client.to_dataframe(records)

    async def create_document(self, data: ProviderDocumentCreate) -> ProviderDocument:
        """Associate a document with a provider.

        Backed by ``POST /api/v1/users/provider-documents/``, now officially
        documented (new spec fields: ``file_checksum``, ``uploaded_date``,
        ``expiration_date``, ``state``). Production still requires JWT Bearer
        auth for this endpoint, which the SDK handles automatically.
        """
        payload = data.model_dump(mode="json", exclude_none=False)
        payload["id"] = ""
        payload["presigned_document_url"] = ""
        resp = await self._client._post(_DOCUMENTS, json=payload, requires_jwt=True)
        return ProviderDocument.model_validate(resp)

    async def upload_and_associate_document(
        self,
        provider_id: str,
        file_content: bytes,
        filename: str,
        document_name: str,
        document_type: str,
        mime_type: str | None = None,
    ) -> ProviderDocument:
        """High-level orchestration: uploads a file to S3 and associates it to a provider.

        This manages both steps of the JWT-authenticated workflow automatically:
        1. Submits file to `/api/v1/files/handle/` (still undocumented) to acquire the S3 storage URI.
        2. Submits association to `/api/v1/users/provider-documents/` (now officially documented).
        """
        import os

        ext = os.path.splitext(filename)[1].lower()
        if ext not in {".pdf", ".png", ".jpg", ".jpeg"}:
            raise ValueError(f"Unsupported file format: '{ext}'. Assured only accepts PDF, PNG, and JPEG files.")

        # Step 1: Upload file to storage backend
        file_record = await self._client.files.upload(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
        )

        if not file_record.file_url:
            from assured.exceptions import AssuredAPIError

            raise AssuredAPIError(
                500,
                f"Failed to extract `file_url` from upload response: {file_record}",
                url=_DOCUMENTS,
            )

        # Step 2: Associate with provider
        doc_create = ProviderDocumentCreate(
            provider=provider_id,
            document_name=document_name,
            document_type=document_type,
            document_url=file_record.file_url,
        )
        return await self.create_document(doc_create)

    # ---- Professional Liability Insurance ----

    async def list_insurance(
        self,
        *,
        provider: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProfessionalLiabilityInsurance]:
        data = await self._client._get_page(_INSURANCE, params=_params(provider, limit, offset))
        return [ProfessionalLiabilityInsurance.model_validate(i) for i in data.get("results", [])]

    async def list_insurance_all(self, *, provider: str | None = None) -> list[ProfessionalLiabilityInsurance]:
        records = await self._client._get_all_pages(_INSURANCE, params=_params(provider))
        return [ProfessionalLiabilityInsurance.model_validate(i) for i in records]

    async def list_insurance_df(self, *, provider: str | None = None) -> pd.DataFrame:
        records = await self._client._get_all_pages(_INSURANCE, params=_params(provider))
        return self._client.to_dataframe(records)

    async def create_insurance(self, data: ProfessionalLiabilityInsuranceCreate) -> dict[str, Any]:
        return await self._client._post(_INSURANCE, json=data.model_dump(mode="json", exclude_none=False))
