from typing import Literal

from pydantic import BaseModel, Field


class AgreementSchema(BaseModel):
    claim: str = Field(description="A factual claim supported by both internal and external evidence.")
    internal_source: str = Field(
        description="Internal source path cited for this agreement.",
    )
    external_source: str = Field(
        description="PubMed PMID cited for this agreement.",
    )


class DisagreementSchema(BaseModel):
    claim_internal: str = Field(description="What the internal evidence states.")
    internal_source: str = Field(description="Internal source path for the internal claim.")
    claim_external: str = Field(description="What the external evidence states.")
    external_source: str = Field(description="PubMed PMID for the external claim.")


class ValidationAssessment(BaseModel):
    in_sync: bool = Field(
        description=(
            "True when internal NovaCrop evidence and external PubMed literature "
            "broadly align on the research question. False when they materially conflict."
        ),
    )
    agreements: list[AgreementSchema] = Field(
        default_factory=list,
        description="Claims supported by both internal and external sources.",
    )
    disagreements: list[DisagreementSchema] = Field(
        default_factory=list,
        description="Material conflicts between internal and external sources.",
    )
    internal_only: list[str] = Field(
        default_factory=list,
        description="Notable findings present only in NovaCrop internal evidence.",
    )
    external_only: list[str] = Field(
        default_factory=list,
        description="Notable findings present only in external PubMed literature.",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence in the validation assessment.",
    )
