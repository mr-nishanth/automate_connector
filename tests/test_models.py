import pytest
from pydantic import ValidationError

from automate_connector.reynolds.models import VehicleRecord

VIN = "1HGCM82633A004352"


def test_parses_contract_fields():
    rec = VehicleRecord.model_validate(
        {"vin": VIN, "make": "Honda", "model": "Accord", "year": 2003}
    )
    assert rec.vin == VIN
    assert rec.make == "Honda"
    assert rec.model == "Accord"
    assert rec.year == 2003
    assert isinstance(rec.year, int)


def test_field_names_are_exact():
    assert set(VehicleRecord.model_fields) == {"vin", "make", "model", "year"}


@pytest.mark.parametrize("missing", ["vin", "make", "model", "year"])
def test_rejects_missing_fields(missing):
    data = {"vin": VIN, "make": "Honda", "model": "Accord", "year": 2003}
    del data[missing]
    with pytest.raises(ValidationError):
        VehicleRecord.model_validate(data)


def test_rejects_non_integer_year():
    with pytest.raises(ValidationError):
        VehicleRecord.model_validate(
            {"vin": VIN, "make": "Honda", "model": "Accord", "year": "2003x"}
        )
