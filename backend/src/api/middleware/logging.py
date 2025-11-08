"""
Request/response logging middleware.

This module provides middleware for logging all API requests and responses
with timing information and context.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.src.utils.logging_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Logs:
    - Request method, path, client host
    - Response status code and processing time
    - Request body size for uploads
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            HTTP response
        """
        # Record start time
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        # Log request
        logger.info(f"→ {method} {path} from {client_host}")

        # Log request body size if present
        if "content-length" in request.headers:
            content_length = int(request.headers["content-length"])
            logger.debug(f"  Request body size: {content_length / 1024:.2f}KB")

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                f"✗ {method} {path} -> ERROR after {processing_time:.2f}ms: {str(e)}"
            )
            raise

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Log response
        status_code = response.status_code
        status_emoji = "✓" if status_code < 400 else "✗"

        logger.info(
            f"{status_emoji} {method} {path} -> {status_code} "
            f"({processing_time_ms:.2f}ms)"
        )

        # Add processing time to response headers
        response.headers["X-Process-Time-Ms"] = f"{processing_time_ms:.2f}"

        return response


def log_request_details(request: Request) -> None:
    """
    Log detailed information about a request.

    Args:
        request: HTTP request to log
    """
    logger.debug("Request details:")
    logger.debug(f"  Method: {request.method}")
    logger.debug(f"  URL: {request.url}")
    logger.debug(f"  Headers: {dict(request.headers)}")
    logger.debug(f"  Client: {request.client.host if request.client else 'unknown'}")


def log_response_details(response: Response, processing_time_ms: float) -> None:
    """
    Log detailed information about a response.

    Args:
        response: HTTP response to log
        processing_time_ms: Time taken to process request
    """
    logger.debug("Response details:")
    logger.debug(f"  Status: {response.status_code}")
    logger.debug(f"  Processing time: {processing_time_ms:.2f}ms")
    logger.debug(f"  Headers: {dict(response.headers)}")


def log_api_call(
    method: str, endpoint: str, params: dict = None, body: dict = None
) -> None:
    """
    Log an API call with parameters and body.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        params: Query parameters
        body: Request body
    """
    logger.debug(f"API Call: {method} {endpoint}")
    if params:
        logger.debug(f"  Params: {params}")
    if body:
        logger.debug(f"  Body: {body}")


def log_api_error(
    method: str, endpoint: str, status_code: int, error_message: str
) -> None:
    """
    Log an API error response.

    Args:
        method: HTTP method
        endpoint: API endpoint path
        status_code: HTTP status code
        error_message: Error message
    """
    logger.error(f"API Error: {method} {endpoint} -> {status_code}: {error_message}")
