"""Stable analysis API boundary."""

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from app.agent.gateway import ModelGateway, OpenAIGateway
from app.agent.graph import run_analysis
from app.query.audit import fail_interaction, start_interaction
from app.query.graph import run_dynamic_analysis

router = APIRouter(prefix="/api/v1", tags=["analysis"])


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None


class AnalysisResponse(BaseModel):
    conversation_id: str
    request_id: str
    answer: str
    key_findings: list[str]
    evidence: list[dict[str, Any]]
    analysis_performed: list[str]
    structured_data: list[dict[str, Any]]
    warnings: list[str]
    status: str


class DynamicAnalysisResponse(AnalysisResponse):
    query: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    result: dict[str, Any] | None = None


def get_model_gateway() -> ModelGateway:
    return OpenAIGateway()


@router.post("/analysis", response_model=AnalysisResponse)
def analyze(
    request: AnalysisRequest,
    response: Response,
    gateway: ModelGateway = Depends(get_model_gateway),
) -> AnalysisResponse:
    conversation_id = request.conversation_id or str(uuid4())
    request_id = str(uuid4())
    response.headers["X-Request-ID"] = request_id
    try:
        result = run_analysis(
            request.question, gateway=gateway, request_id=request_id
        )
        return AnalysisResponse.model_validate(
            {**result, "conversation_id": conversation_id}
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="analysis service unavailable",
            headers={"X-Request-ID": request_id},
        ) from error


@router.post("/dynamic-analysis", response_model=DynamicAnalysisResponse)
def analyze_dynamic(
    request: AnalysisRequest,
    response: Response,
) -> DynamicAnalysisResponse:
    """Run the Slice 10 coordinator with dynamic SQL guardrails."""

    conversation_id = request.conversation_id or str(uuid4())
    request_id = str(uuid4())
    response.headers["X-Request-ID"] = request_id
    start_interaction(
        request_id=request_id,
        question=request.question,
        conversation_id=conversation_id,
    )
    try:
        result = run_dynamic_analysis(
            request.question,
            request_id=request_id,
            conversation_id=conversation_id,
        )
        return DynamicAnalysisResponse.model_validate(
            {**result, "conversation_id": conversation_id}
        )
    except Exception as error:
        fail_interaction(request_id=request_id, stage="api", error=error)
        raise HTTPException(
            status_code=502,
            detail="dynamic analysis service unavailable",
            headers={"X-Request-ID": request_id},
        ) from error
