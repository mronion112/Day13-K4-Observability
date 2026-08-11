from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    from langfuse import get_client, observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    def propagate_attributes(*args: Any, **kwargs: Any):
        class DummyContext:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

        return DummyContext()

    class _DummyClient:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

        def get_prompt(self, *args: Any, **kwargs: Any):
            return None

        def flush(self) -> None:
            return None

    def get_client():
        return _DummyClient()


class LangfuseClientAdapter:
    def __init__(self, client: Any) -> None:
        self._client = client

    def update_current_trace(self, **kwargs: Any) -> None:
        """
        Compatibility layer for the old update_current_trace API.

        Langfuse v3/v4 exposes update_current_span instead.
        """
        update_current_span = getattr(
            self._client,
            "update_current_span",
            None,
        )

        if callable(update_current_span):
            update_current_span(**kwargs)
            return

        update_current_trace = getattr(
            self._client,
            "update_current_trace",
            None,
        )

        if callable(update_current_trace):
            update_current_trace(**kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


def get_langfuse_client():
    return LangfuseClientAdapter(get_client())


def tracing_enabled() -> bool:
    return (
        LANGFUSE_SDK_AVAILABLE
        and bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
        and bool(os.getenv("LANGFUSE_SECRET_KEY"))
    )
