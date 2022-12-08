from pydantic import BaseModel


class TenantSchema(BaseModel):
    houseId: int
    firstName: str
    lastName: str
    phoneNumber: str
    email: str
    password: str
    state: str
    deviceId: str
    profileURL: str


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
