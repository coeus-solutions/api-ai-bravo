from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TimestampModel(BaseModel):
    created_at: datetime
    updated_at: datetime

class BaseDBModel(BaseModel):
    model_config = ConfigDict(from_attributes=True) 