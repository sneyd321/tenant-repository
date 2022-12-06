from pydantic import BaseModel


class TenantSchema(BaseModel):
    profileURL: str
    houseId: int
    firstName: str
    lastName: str
    email: str
    password: str
    tenantState: str
    deviceId: str


class TempTenantSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    houseId: int


class LoginSchema(BaseModel):
    email: str
    password: str
    houseId: int
    deviceId: str
