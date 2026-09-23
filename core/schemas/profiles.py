from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

class ProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("must not be empty or whitespace")
        # letters, spaces, hyphens, apostrophes (covers most real names)
        if not re.fullmatch(r"[A-Za-z\u00C0-\u017F' -]+", v):
            raise ValueError("must contain only letters, spaces, hyphens, or apostrophes")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        # allow leading + then digits, spaces, dashes, parens
        if not re.fullmatch(r"\+?[0-9\s\-()]{7,20}", v):
            raise ValueError("invalid phone number format")
        digit_count = len(re.sub(r"\D", "", v))
        if not (7 <= digit_count <= 15):  # E.164 max is 15 digits
            raise ValueError("phone number must have between 7 and 15 digits")
        return v

class ProfileResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    updated_date: datetime
