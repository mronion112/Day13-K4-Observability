from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio
from app.prompt_management import DEFAULT_PROMPT_TEMPLATE
from app.tracing import get_langfuse_client, tracing_enabled


BASELINE_PROMPT = (
    "You are a concise AI operations assistant. Use the supplied documents when relevant.\n"
    + DEFAULT_PROMPT_TEMPLATE
    + "\nAnswer clearly and do not repeat sensitive personal data."
)

CANDIDATE_PROMPT = (
    "You are a concise AI operations assistant. Use only evidence supported by the supplied documents.\n"
    + DEFAULT_PROMPT_TEMPLATE
    + "\nAnswer in at most three short bullet points and do not repeat sensitive personal data."
)


def _get_prompt(client, name: str, label: str):
    try:
        return client.get_prompt(
            name,
            label=label,
            type="text",
            cache_ttl_seconds=0,
            fetch_timeout_seconds=5,
            max_retries=0,
        )
    except NotFoundError:
        return None


def main() -> int:
    configure_utf8_stdio()
    load_dotenv(REPO_ROOT / ".env")
    if not tracing_enabled():
        print("Thiếu LANGFUSE_PUBLIC_KEY hoặc LANGFUSE_SECRET_KEY trong .env")
        return 1

    client = get_langfuse_client()
    name = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")
    baseline = _get_prompt(client, name, "baseline")
    candidate = _get_prompt(client, name, "candidate")

    if baseline is None:
        baseline = client.create_prompt(
            name=name,
            prompt=BASELINE_PROMPT,
            labels=["baseline", "production"],
            tags=["day13", "observability"],
            type="text",
            commit_message="Day 13 baseline prompt",
        )
        print(f"Đã tạo baseline/production version {baseline.version}")
    else:
        print(f"Baseline đã tồn tại ở version {baseline.version}")

    if candidate is None:
        candidate = client.create_prompt(
            name=name,
            prompt=CANDIDATE_PROMPT,
            labels=["candidate"],
            tags=["day13", "observability"],
            type="text",
            commit_message="Day 13 candidate: concise bullet format",
        )
        print(f"Đã tạo candidate version {candidate.version}")
    else:
        print(f"Candidate đã tồn tại ở version {candidate.version}")

    print(f"Prompt {name}: baseline=v{baseline.version}, candidate=v{candidate.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
