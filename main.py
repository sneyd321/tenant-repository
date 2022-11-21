from fastapi import FastAPI, HTTPException
from models.schemas import TenantSchema, LoginSchema, TempTenantSchema, TenantStateSchema
from models.db import DB
from models.models import Tenant
from models.repository import Repository
import uvicorn, os

user = os.environ.get('DB_USER', "test")
password = os.environ.get('DB_PASS', "homeowner")
host = os.environ.get('DB_HOST', "localhost")
database = os.environ.get('DB_DATABASE', "roomr")

db = DB(user, password, host, database)
repository = Repository(db)
app = FastAPI()


@app.get("/Health")
async def health_check():
    return {"status": 200}


@app.post("/Tenant")
async def create_tenant(request: TempTenantSchema):
    tenant = Tenant(**request.dict(), password="", tenantState="Temp_Account_Created")
    monad = await repository.insert_temp(tenant)
    if monad.has_errors():
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return monad.get_param_at(0).to_json()

@app.put("/Tenant/{tenantState}")
async def update_tenant_state(tenantState: str, request: TenantStateSchema):
    tenant = Tenant(**request.dict(), tenantState=tenantState)
    monad = await repository.update_tenant(tenant, tenantState)
    if monad.has_errors():
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return monad.get_param_at(0).to_json()
    
@app.post("/Login")
async def login(request: LoginSchema):
    loginData = request.dict()
    tenant = Tenant(**loginData)
    monad = await repository.login(tenant, loginData["password"])
    if monad.has_errors():
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return monad.get_param_at(0).to_json()


@app.get("/House/{houseId}/Tenant")
async def get_tenants_by_house_id(houseId: int):
    tenant = Tenant(password="", houseId=houseId)
    monad = await repository.get_tenants_by_house_id(tenant)
    if monad.has_errors():
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return [tenant.to_json() for tenant in monad.get_param_at(0)]


@app.delete("/Tenant")
async def delete_tenant(request: TenantSchema):
    tenant = Tenant(**request.dict())
    monad = await repository.delete_tenant(tenant)
    if monad.has_errors():
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return monad.get_param_at(0).to_json()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8085)
