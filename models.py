from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
from sqlalchemy import JSON, Column
from sqlmodel import SQLModel, Field, Relationship
from typing import Dict, Any
import hashlib


class StringRequestBody(SQLModel):
    value: str


class StringProperty(SQLModel, table=True):
    id: str = Field(primary_key=True, description="SHA 256 hash of the string value")
    value: str = Field(..., description="String to analyze")
    properties: Dict[str, Any] = Field(sa_column=Column(JSON),
                                       description="Properties of the analyzed string")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def generate_hash(value: str) -> str:
        """Generate SHA-256 hash from the given string."""
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
    
    @classmethod
    def create(cls, value: str, properties: Dict[str, Any]):
        """Factory method to automatically generate the hash id."""
        return cls(
            id=cls.generate_hash(value),
            value=value,
            properties=properties
        )