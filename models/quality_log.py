from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum
from pydantic import BeforeValidator
from typing import Annotated

class QualityStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"

def validate_object_id(v):
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class QualityLogCreate(BaseModel):
    status: QualityStatus
    details: Optional[str] = Field(None, max_length=1000)

class QualityLogResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    dataset_id: PyObjectId
    status: QualityStatus
    details: Optional[str]
    timestamp: datetime
