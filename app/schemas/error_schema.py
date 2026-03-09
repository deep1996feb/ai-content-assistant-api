from pydantic import BaseModel

class Errorresponse(BaseModel):
    message: str
    success: bool = False