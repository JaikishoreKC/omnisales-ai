from typing import Any, Dict, Optional


def api_success(data: Optional[Any] = None, message: str = "") -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "success": True,
        "data": data,
        "message": message,
        "error": None
    }

    if isinstance(data, dict):
        response.update(data)

    return response


def api_error(message: str, error: Optional[str] = None, data: Optional[Any] = None) -> Dict[str, Any]:
    return {
        "success": False,
        "data": data,
        "message": message,
        "error": error or message
    }
