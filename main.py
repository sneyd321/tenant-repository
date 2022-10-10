from fastapi import FastAPI
from models.schemas import *
from models.db import DB
from models.models import Tenant
from models.repository import Repository
import uvicorn, os, json

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
async def create_tenant(request: TenantSchema):
    tenant = Tenant(**request.dict())
    monad = await repository.insert(tenant)
    if monad.error_status:
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return tenant.to_json()

@app.post("/Login")
async def login(request: LoginSchema):
    loginData = request.dict()
    tenant = Tenant(**loginData)
    monad = await repository.login(tenant, loginData["password"])
    if monad.error_status:
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return monad.data.to_json()

@app.get("/House/{houseId}/Tenant")
async def get_tenants_by_house_id(houseId: int):
    tenant = Tenant(password="", houseId=houseId)
    monad = await repository.get_tenants_by_house_id(tenant)
    if monad.error_status:
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return [tenant.to_json() for tenant in monad.data]


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8085)