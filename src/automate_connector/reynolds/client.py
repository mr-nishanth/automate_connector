"""HTTP client for GET /vehicles/{vin} on reynolds-connector."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from automate_connector.reynolds.errors import (
    InvalidResponseError,
    ReynoldsError,
    ReynoldsServerError,
    ReynoldsTransportError,
    VehicleNotFoundError,
)
from automate_connector.reynolds.models import VehicleRecord


class _RetryableServerError(Exception):
    """Internal marker for HTTP 5xx responses that should be retried."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"server returned HTTP {status_code}")
        self.status_code = status_code


class ReynoldsClient:
    """Client for the reynolds-connector vehicle lookup endpoint.

    Retries 5xx responses and timeouts/transport errors with exponential
    backoff. 404 and other 4xx responses are never retried.
    """

    def __init__(
        self,
        base_url: str,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 10.0,
        max_attempts: int = 3,
        wait_seconds: Any = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self._max_attempts = max_attempts
        self._wait = wait_seconds if wait_seconds is not None else wait_exponential(
            multiplier=0.5, min=0.5, max=8
        )
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            transport=transport,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ReynoldsClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def get_vehicle(self, vin: str) -> VehicleRecord:
        """Look up a vehicle by VIN and return a validated VehicleRecord."""
        retrying = Retrying(
            stop=stop_after_attempt(self._max_attempts),
            wait=self._wait,
            retry=retry_if_exception_type(
                (_RetryableServerError, httpx.TimeoutException, httpx.TransportError)
            ),
            reraise=True,
        )
        try:
            response = retrying(self._request_once, vin)
        except _RetryableServerError as exc:
            raise ReynoldsServerError(
                f"Reynolds API returned HTTP {exc.status_code} for VIN lookup "
                f"after {self._max_attempts} attempt(s)"
            ) from None
        except httpx.TimeoutException as exc:
            raise ReynoldsTransportError(
                f"Reynolds API timed out after {self._max_attempts} attempt(s)"
            ) from exc
        except httpx.TransportError as exc:
            raise ReynoldsTransportError(
                f"Reynolds API transport failure after {self._max_attempts} attempt(s): "
                f"{type(exc).__name__}"
            ) from exc

        return self._parse(response)

    def _request_once(self, vin: str) -> httpx.Response:
        response = self._client.get(f"/vehicles/{vin}")
        if response.status_code >= 500:
            raise _RetryableServerError(response.status_code)
        return response

    @staticmethod
    def _parse(response: httpx.Response) -> VehicleRecord:
        status = response.status_code
        if status == 404:
            raise VehicleNotFoundError("Vehicle not found in Reynolds for the given VIN")
        if status == 422:
            raise ReynoldsError("Reynolds API rejected the VIN as invalid (HTTP 422)")
        if 400 <= status < 500:
            raise ReynoldsError(f"Reynolds API returned unexpected HTTP {status}")
        if status != 200:
            raise InvalidResponseError(f"Reynolds API returned unexpected HTTP {status}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise InvalidResponseError("Reynolds API returned a non-JSON body") from exc

        try:
            return VehicleRecord.model_validate(payload)
        except ValidationError as exc:
            fields = sorted({".".join(str(p) for p in e["loc"]) or "<root>" for e in exc.errors()})
            raise InvalidResponseError(
                "Reynolds API response does not match VehicleRecord; "
                f"invalid fields: {', '.join(fields)}"
            ) from exc
