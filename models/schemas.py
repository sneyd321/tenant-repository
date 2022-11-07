from pydantic import BaseModel


class TenantSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str


class TempTenantSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    houseId: int


class TenantStateSchema(BaseModel):
    firstName: str
    lastName: str
    email: str


class LoginSchema(BaseModel):
    email: str
    password: str
    houseId: int
    deviceId: str
