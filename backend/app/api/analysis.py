"""Stable analysis API boundary."""

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.agent.gateway import ModelGateway, OpenAIGateway
from app.agent.graph import run_analysis

router = APIRouter(prefix="/api/v1", tags=["analysis"])


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None


class AnalysisResponse(BaseModel):
    request_id: str
    answer: str
    key_findings: list[str]
    evidence: list[dict[str, Any]]
    analysis_performed: list[str]
    structured_data: list[dict[str, Any]]
    warnings: list[str]
    status: str


def get_model_gateway() -> ModelGateway:
    return OpenAIGateway()


@router.post("/analysis", response_model=AnalysisResponse)
def analyze(
    request: AnalysisRequest, gateway: ModelGateway = Depends(get_model_gateway)
) -> AnalysisResponse:
    try:
        result = run_analysis(
            request.question, gateway=gateway, request_id=str(uuid4())
        )
        return AnalysisResponse.model_validate(result)
    except Exception as error:
        raise HTTPException(
            status_code=502, detail="analysis service unavailable"
        ) from error
