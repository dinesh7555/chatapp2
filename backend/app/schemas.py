from pydantic import BaseModel, EmailStr
from typing import List
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str 
    token_type: str = "bearer"

 

class ChatMessageRequest(BaseModel):
    conversation_id: str
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]