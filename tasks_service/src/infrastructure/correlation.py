from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from uuid import UUID, uuid4

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


_correlation_id: ContextVar[UUID | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> UUID | None:
    return _correlation_id.get()


@contextmanager
def correlation_context(correlation_id: UUID) -> Iterator[None]:
    token = _correlation_id.set(correlation_id)

    try:
        with structlog.contextvars.bound_contextvars(correlation_id=str(correlation_id)):
            yield
    finally:
        _correlation_id.reset(token)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        header_value = request.headers.get("X-Correlation-ID")

        try:
            correlation_id = UUID(header_value) if header_value is not None else uuid4()
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "X-Correlation-ID must be a UUID"})

        with correlation_context(correlation_id):
            response = await call_next(request)

            structlog.get_logger(__name__).info(
                "HTTP request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )

        response.headers["X-Correlation-ID"] = str(correlation_id)
        return response