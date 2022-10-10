from typing import Set, Union, List
from pydantic import BaseModel


class TenantSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str
    tenantState: str
    houseId: int

class LoginSchema(BaseModel):
    email: str
    password: str
    houseId: int
    deviceId: str
