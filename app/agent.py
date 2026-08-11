from __future__ import annotations

import time
from dataclasses import dataclass

from structlog.contextvars import get_contextvars

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .prompt_management import resolve_prompt
from .tracing import (
    get_langfuse_client,
    observe,
    propagate_attributes,
    tracing_enabled,
)


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(
        as_type="generation",
        capture_input=False,
        capture_output=False,
    )
    def run(
        self,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
    ) -> AgentResult:

        correlation_id = get_contextvars().get(
            "correlation_id",
            "MISSING",
        )

        # Langfuse observability must never break the application request.
        langfuse_client = get_langfuse_client()

        try:
            with propagate_attributes(
                user_id=hash_user_id(user_id),
                session_id=session_id,
                tags=[
                    "lab",
                    feature,
                    self.model,
                ],
                metadata={
                    "correlation_id": correlation_id,
                    "feature": feature,
                    "model": self.model,
                },
            ):
                return self._run_agent(
                    user_id=user_id,
                    feature=feature,
                    session_id=session_id,
                    message=message,
                    langfuse_client=langfuse_client,
                )

        except Exception:
            # Observability failure must never fail the application request.
            return self._run_agent(
                user_id=user_id,
                feature=feature,
                session_id=session_id,
                message=message,
                langfuse_client=langfuse_client,
                enable_langfuse=False,
            )

    def _run_agent(
        self,
        *,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
        langfuse_client,
        enable_langfuse: bool = True,
    ) -> AgentResult:

        started = time.perf_counter()

        # Include RAG latency in the measured request latency.
        docs = retrieve(message)

        prompt = resolve_prompt(
            langfuse_client,
            feature=feature,
            docs=docs,
            message=message,
            enabled=tracing_enabled() and enable_langfuse,
        )

        response = self.llm.generate(prompt.text)

        quality_score = self._heuristic_quality(
            message,
            response.text,
            docs,
        )

        latency_ms = int(
            (time.perf_counter() - started) * 1000
        )

        cost_usd = self._estimate_cost(
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        if enable_langfuse:
            try:
                prompt_metadata = {
                    "prompt_name": prompt.name,
                    "prompt_label": prompt.label,
                    "prompt_version": prompt.version,
                    "prompt_source": prompt.source,
                }

                # Trace-level metadata.
                langfuse_client.update_current_trace(
                    metadata=prompt_metadata,
                )

                # Generation-level metadata.
                langfuse_client.update_current_generation(
                    model=self.model,
                    metadata={
                        "doc_count": len(docs),
                        "query_preview": summarize_text(message),
                        "prompt_name": prompt.name,
                        "prompt_label": prompt.label,
                        "prompt_version": prompt.version,
                        "prompt_source": prompt.source,
                        "prompt_fetch_error": prompt.fetch_error,
                    },
                    usage_details={
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                    },
                    cost_details={
                        "total": cost_usd,
                    },
                    prompt=prompt.managed_prompt,
                )

            except Exception:
                # Observability failure must never fail the user request.
                pass

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(
        self,
        tokens_in: int,
        tokens_out: int,
    ) -> float:
        input_cost = (
            tokens_in / 1_000_000
        ) * 3

        output_cost = (
            tokens_out / 1_000_000
        ) * 15

        return round(
            input_cost + output_cost,
            6,
        )

    def _heuristic_quality(
        self,
        question: str,
        answer: str,
        docs: list[str],
    ) -> float:
        score = 0.5

        if docs:
            score += 0.2

        if len(answer) > 40:
            score += 0.1

        question_tokens = question.lower().split()

        if (
            question_tokens
            and any(
                token in answer.lower()
                for token in question_tokens[:3]
            )
        ):
            score += 0.1

        if "[REDACTED" in answer:
            score -= 0.2

        return round(
            max(
                0.0,
                min(1.0, score),
            ),
            2,
        )
