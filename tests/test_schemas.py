import pytest
from pydantic import ValidationError
from app.schemas import ProductInput


def test_valid_product():
    product = ProductInput(name="Манометр", specs={"диапазон": "0–1 МПа"})
    assert product.name == "Манометр"
    assert product.specs["диапазон"] == "0–1 МПа"


def test_blank_name_rejected():
    with pytest.raises(ValidationError):
        ProductInput(name="   ")


def test_missing_optional_fields_are_allowed():
    product = ProductInput(name="Прибор")
    assert product.manufacturer is None
    assert product.specs == {}
