from pydantic import BaseModel, Field, field_validator
from typing import Any


class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=250, description="Название товара")
    manufacturer: str | None = Field(default=None, max_length=200)
    specs: dict[str, Any] = Field(default_factory=dict)
    description: str | None = Field(default=None, max_length=12000)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Название товара не должно быть пустым")
        return value.strip()


class ProductCard(BaseModel):
    seo_title: str
    seo_description: str
    key_characteristics: dict[str, str]
    search_queries: list[str]
    commercial_block: str
    missing_data: list[str] = Field(default_factory=list)
    clarification_notes: list[str] = Field(default_factory=list)
