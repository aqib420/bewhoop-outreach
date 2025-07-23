from pydantic import BaseModel, EmailStr
from typing import Optional, List

class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    is_html: Optional[bool] = False
