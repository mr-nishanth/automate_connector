import json

import httpx
import pytest
from tenacity import wait_none

from automate_connector.reynolds import (
    InvalidResponseError,
    ReynoldsClient,
    ReynoldsError,
    ReynoldsServerError,
    ReynoldsTransportError,
    VehicleNotFoundError,
    VehicleRecord,
)

BASE = "http://reynolds.test"
VIN = "1HGCM82633A004352"
OK_BODY = {"vin": VIN, "make": "Honda", "model": "Accord", "year": 2003}


def make_client(handler, max_attempts=3):
    transport = httpx.MockTransport(handler)
    return ReynoldsClient(
        BASE, transport=transport, max_attempts=max_attempts, wait_seconds=wait_none()
    )


def test_success_parses_into_vehicle_record():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=OK_BODY)

    with make_client(handler) as client:
        rec = client.get_vehicle(VIN)

    assert isinstance(rec, VehicleRecord)
    assert rec == VehicleRecord(**OK_BODY)
    assert len(seen) == 1
    assert seen[0].method == "GET"
    assert seen[0].url.path == f"/vehicles/{VIN}"


def test_lowercase_vin_is_passed_through_for_server_normalisation():
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(200, json=OK_BODY)

    with make_client(handler) as client:
        client.get_vehicle(VIN.lower())

    assert seen == [f"/vehicles/{VIN.lower()}"]


def test_404_raises_vehicle_not_found_without_retry():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(404, json={"detail": "Vehicle not found"})

    with make_client(handler) as client:
        with pytest.raises(VehicleNotFoundError, match="not found"):
            client.get_vehicle(VIN)
    assert len(calls) == 1


def test_422_raises_reynolds_error_without_retry():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(422, json={"detail": [{"msg": "bad vin"}]})

    with make_client(handler) as client:
        with pytest.raises(ReynoldsError) as excinfo:
            client.get_vehicle("BAD")
    assert not isinstance(excinfo.value, VehicleNotFoundError)
    assert len(calls) == 1


def test_5xx_is_retried_then_succeeds():
    responses = [httpx.Response(503), httpx.Response(500), httpx.Response(200, json=OK_BODY)]
    calls = []

    def handler(request):
        calls.append(request)
        return responses.pop(0)

    with make_client(handler, max_attempts=3) as client:
        rec = client.get_vehicle(VIN)
    assert rec.vin == VIN
    assert len(calls) == 3


def test_5xx_exhausted_raises_server_error():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(502)

    with make_client(handler, max_attempts=3) as client:
        with pytest.raises(ReynoldsServerError, match="502"):
            client.get_vehicle(VIN)
    assert len(calls) == 3


def test_timeout_is_retried_then_succeeds():
    attempts = {"n": 0}

    def handler(request):
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise httpx.ReadTimeout("timed out", request=request)
        return httpx.Response(200, json=OK_BODY)

    with make_client(handler, max_attempts=3) as client:
        rec = client.get_vehicle(VIN)
    assert rec.make == "Honda"
    assert attempts["n"] == 2


def test_timeout_exhausted_raises_transport_error():
    attempts = {"n": 0}

    def handler(request):
        attempts["n"] += 1
        raise httpx.ConnectTimeout("timed out", request=request)

    with make_client(handler, max_attempts=2) as client:
        with pytest.raises(ReynoldsTransportError, match="timed out"):
            client.get_vehicle(VIN)
    assert attempts["n"] == 2


def test_invalid_json_raises_invalid_response():
    def handler(request):
        return httpx.Response(200, content=b"<html>not json</html>")

    with make_client(handler) as client:
        with pytest.raises(InvalidResponseError, match="non-JSON"):
            client.get_vehicle(VIN)


@pytest.mark.parametrize(
    "body",
    [
        {"vin": VIN, "make": "Honda", "model": "Accord"},  # missing year
        {"vin": VIN, "make": "Honda", "model": "Accord", "year": "two thousand"},
        {"vin": "short", "make": "Honda", "model": "Accord", "year": 2003},
        ["not", "an", "object"],
    ],
)
def test_malformed_200_body_raises_invalid_response(body):
    def handler(request):
        return httpx.Response(200, content=json.dumps(body).encode())

    with make_client(handler) as client:
        with pytest.raises(InvalidResponseError):
            client.get_vehicle(VIN)


def test_no_transport_uses_real_client_only_when_constructed_without_mock():
    # Constructing without a transport must not perform any request.
    client = ReynoldsClient(BASE, wait_seconds=wait_none())
    try:
        assert client._client.base_url.host == "reynolds.test"
    finally:
        client.close()


def test_invalid_max_attempts_rejected():
    with pytest.raises(ValueError):
        ReynoldsClient(BASE, max_attempts=0)
