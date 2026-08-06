from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class CheckAccountSchema(BaseModel):
    email: EmailStr
