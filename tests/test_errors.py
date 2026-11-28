import pytest

from automate_connector.reynolds.errors import (
    InvalidResponseError,
    ReynoldsError,
    ReynoldsServerError,
    ReynoldsTransportError,
    VehicleNotFoundError,
)


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (ReynoldsError, False),
        (VehicleNotFoundError, False),
        (ReynoldsServerError, True),
        (ReynoldsTransportError, True),
        (InvalidResponseError, False),
    ],
)
def test_retryable_value_per_error_class(cls, expected):
    assert cls.retryable is expected


@pytest.mark.parametrize(
    "cls",
    [
        VehicleNotFoundError,
        ReynoldsServerError,
        ReynoldsTransportError,
        InvalidResponseError,
    ],
)
def test_subclasses_inherit_from_reynolds_error(cls):
    assert issubclass(cls, ReynoldsError)
