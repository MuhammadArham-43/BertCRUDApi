from typing import Optional, Literal
from pydantic import BaseModel, PositiveInt
from fastapi import Form, UploadFile


class ReviewInputParameters(BaseModel):
    comment_id: PositiveInt
    campaign_id: PositiveInt
    description: str
    sentiment: Optional[Literal["positive", "negative"]] = None
    
class PredictParameters(BaseModel):
    description: str
    
class ReviewDeleteParameters(BaseModel):
    comment_id: PositiveInt
    
class BulkInsertInputParameters(BaseModel):
    document: UploadFile = Form(...)