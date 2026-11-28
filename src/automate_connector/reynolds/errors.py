"""Error types raised by the Reynolds client."""


class ReynoldsError(Exception):
    """Base error for Reynolds client failures.

    ``retryable`` marks whether a failure is safe to retry. It defaults to
    False; subclasses for transient failures override it to True.
    """

    retryable: bool = False


class VehicleNotFoundError(ReynoldsError):
    """The requested VIN is well-formed but unknown (HTTP 404)."""


class ReynoldsServerError(ReynoldsError):
    """Server kept returning 5xx responses after all retry attempts."""

    retryable = True


class ReynoldsTransportError(ReynoldsError):
    """Timeouts or transport failures persisted after all retry attempts."""

    retryable = True


class InvalidResponseError(ReynoldsError):
    """A response could not be parsed into the expected contract shape."""
