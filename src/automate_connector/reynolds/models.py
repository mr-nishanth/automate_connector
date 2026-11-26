"""Typed models matching the reynolds-connector API contract."""

from pydantic import BaseModel, ConfigDict, Field


class VehicleRecord(BaseModel):
    """Vehicle record returned by GET /vehicles/{vin}."""

    model_config = ConfigDict(extra="ignore")

    vin: str = Field(min_length=17, max_length=17, pattern=r"^[A-Z0-9]{17}$")
    make: str
    model: str
    year: int
