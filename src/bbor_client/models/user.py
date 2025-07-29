from pydantic import field_validator, model_validator, Field
from datetime import datetime, timedelta, timezone
from .base import ClientModel


class GroupResponse(ClientModel):
    id: str
    abbr: str

    @field_validator('id', mode='before')
    def pydanticobjectid_to_string(cls, value):
        return str(value)
      

class UserResponse(ClientModel):
    id: str
    name: str
    group: GroupResponse
    disabled: bool = False
    created_at: datetime
    updated_at: datetime

