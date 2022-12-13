from pydantic import BaseModel


class TenantSchema(BaseModel):
    firstName: str
    lastName: str
    phoneNumber: str
    email: str
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
