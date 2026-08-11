from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Xóa contextvars cũ — tránh dữ liệu từ request trước bị rò rỉ sang request sau
        clear_contextvars()

        # Trích xuất correlation_id từ header "x-request-id" nếu có
        # Nếu không có, tự sinh mới: format "req-" + 8 ký tự hex ngẫu nhiên
        correlation_id = request.headers.get(
            "x-request-id",
            f"req-{uuid.uuid4().hex[:8]}",
        )

        # Gắn correlation_id vào structlog contextvars
        # để mọi log trong request này đều tự động có trường correlation_id
        bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id

        # Đo thời gian xử lý request (tính bằng ms)
        start = time.perf_counter()
        response = await call_next(request)

        # Thêm correlation_id và thời gian xử lý vào response headers
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"

        return response
