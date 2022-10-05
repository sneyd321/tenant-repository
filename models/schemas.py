from typing import Set, Union, List
from pydantic import BaseModel


class CreateTenantSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str
    tenantState: str

class LoginSchema(BaseModel):
    email: str
    password: str
    houseId: int
    deviceId: str
