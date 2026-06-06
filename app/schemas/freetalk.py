from pydantic import BaseModel

class FreeTalkRequest(BaseModel):
    text: str

class FreeTalkResponseData(BaseModel):
    aiText: str
    targetRole: str

class FreeTalkResponse(BaseModel):
    success: bool
    data: FreeTalkResponseData
