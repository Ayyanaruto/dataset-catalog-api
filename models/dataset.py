from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic import BeforeValidator

def validate_object_id(v):
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    owner: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)

class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    owner: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None

class DatasetResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    name: str
    owner: str
    description: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
