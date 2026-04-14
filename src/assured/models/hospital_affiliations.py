"""Hospital affiliation models."""

from __future__ import annotations

from pydantic import BaseModel

# ---- Admitting Arrangements ----


class AdmittingArrangement(BaseModel):
    id: str | None = None
    hospital_name: str | None = None
    arrangement_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    provider: str | None = None


class AdmittingArrangementCreate(BaseModel):
    provider: str
    hospital_name: str | None = None
    arrangement_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# ---- Admitting Privileges ----


class AdmittingPrivilege(BaseModel):
    id: str | None = None
    hospital_name: str | None = None
    privilege_type: str | None = None
    status: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    provider: str | None = None


class AdmittingPrivilegeCreate(BaseModel):
    provider: str
    hospital_name: str | None = None
    privilege_type: str | None = None
    status: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# ---- Non-Admitting Affiliations ----


class NonAdmittingAffiliation(BaseModel):
    id: str | None = None
    hospital_name: str | None = None
    affiliation_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    provider: str | None = None


class NonAdmittingAffiliationCreate(BaseModel):
    provider: str
    hospital_name: str | None = None
    affiliation_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class HospitalAffiliationListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    provider: str | None = None
