from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ✅ Xóa contextvars cũ — tránh dữ liệu từ request trước bị rò rỉ sang request sau
        #   clear_contextvars() xóa tất cả context đã bind trước đó (correlation_id, user_id_hash, ...)
        #   để mỗi request bắt đầu với context sạch, không bị lẫn dữ liệu
        clear_contextvars()

        # ✅ Trích xuất correlation_id từ header "x-request-id" nếu có, nếu không thì tự sinh mới
        #   Dùng header từ client gửi lên để hỗ trợ distributed tracing
        #   Nếu không có header, sinh mới: format "req-" + 8 ký tự hex (vd: req-a1b2c3d4)
        #   uuid.uuid4().hex[:8] tạo chuỗi hex 8 ký tự ngẫu nhiên
        correlation_id = request.headers.get(
            "x-request-id",
            f"req-{uuid.uuid4().hex[:8]}",
        )

        # ✅ Gắn correlation_id vào structlog contextvars
        #   bind_contextvars() đưa correlation_id vào context toàn cục của structlog
        #   để mọi log trong request này đều tự động có trường correlation_id
        bind_contextvars(correlation_id=correlation_id)

        # Lưu correlation_id vào request.state để các handler khác (như /chat) có thể đọc sau
        request.state.correlation_id = correlation_id

        # Đo thời gian xử lý request (tính bằng ms)
        start = time.perf_counter()
        response = await call_next(request)

        # ✅ Thêm correlation_id và thời gian xử lý vào response headers
        #   Các header này giúp client/load test biết được request nào tương ứng với log nào
        #   x-response-time-ms được tính bằng (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"

        return response
