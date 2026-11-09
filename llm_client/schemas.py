from typing import Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """ Solo aceptamos `system`, `user` o `assistant`. """
    role: Literal["system", "user", "assistant"]
    content: str 
    
class ModelConfig(BaseModel):
    model: str
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=512, gt=0)
    
""" Resp formateada, consistente entre proveedores. """
class ModelResponse(BaseModel):
    text: str
    provider: str
    model: str