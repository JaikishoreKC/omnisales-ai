import contextvars
import logging
from typing import Optional

_request_id_ctx = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        return True


def set_request_id(request_id: str) -> contextvars.Token:
    return _request_id_ctx.set(request_id)


def reset_request_id(token: Optional[contextvars.Token]) -> None:
    if token is not None:
        _request_id_ctx.reset(token)
