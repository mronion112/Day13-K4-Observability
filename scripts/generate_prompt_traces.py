from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from structlog.contextvars import bind_contextvars, clear_contextvars

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.agent import LabAgent
from app.cli import configure_utf8_stdio
from app.logging_config import configure_logging
from app.pii import hash_user_id
from app.tracing import get_langfuse_client, tracing_enabled


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Generate comparable prompt-version traces")
    parser.add_argument("--labels", nargs="+", default=["baseline", "candidate"])
    parser.add_argument(
        "--message",
        default="Explain why metrics, traces, and logs work together.",
    )
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    configure_logging()
    if not tracing_enabled():
        print("Tracing chưa bật; kiểm tra LANGFUSE_PUBLIC_KEY và LANGFUSE_SECRET_KEY")
        return 1

    client = get_langfuse_client()
    prompt_name = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")
    agent = LabAgent()
    for label in args.labels:
        managed_prompt = client.get_prompt(
            prompt_name,
            label=label,
            type="text",
            cache_ttl_seconds=0,
            fetch_timeout_seconds=20,
            max_retries=2,
        )
        os.environ["LANGFUSE_PROMPT_LABEL"] = label
        trace_id = client.create_trace_id(seed=f"day13-{prompt_name}-{label}")
        correlation_id = f"req-{trace_id[:8]}"
        clear_contextvars()
        bind_contextvars(
            correlation_id=correlation_id,
            user_id_hash=hash_user_id("prompt-evidence-user"),
            session_id="prompt-version-comparison",
            feature="monitoring",
            model=agent.model,
            env=os.getenv("APP_ENV", "dev"),
        )
        print(
            f"Đang tạo trace label={label} version={managed_prompt.version} "
            f"trace_id={trace_id}",
            flush=True,
        )
        agent.run(
            user_id="prompt-evidence-user",
            feature="monitoring",
            session_id="prompt-version-comparison",
            message=args.message,
            langfuse_trace_id=trace_id,
        )
        print(
            f"label={label} version={managed_prompt.version} "
            f"trace_id={trace_id} correlation_id={correlation_id} "
            f"url={client.get_trace_url(trace_id=trace_id)}",
            flush=True,
        )

    client.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
