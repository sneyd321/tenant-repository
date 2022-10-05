from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List
from models.schemas import *
from models.db import DB
from models.models import Tenant
from models.repository import Repository
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError


import uvicorn, os, json, requests, asyncio


user = os.environ.get('DB_USER', "root")
password = os.environ.get('DB_PASS', "root")
host = os.environ.get('DB_HOST', "localhost")
database = os.environ.get('DB_DATABASE', "roomr")

db = DB(user, password, host, database)
repository = Repository(db)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    try:
        await repository.create_all()
    except OperationalError:
        SystemExit()

@app.get("/Health")
async def health_check():
    return {"status": 200}

@app.post("/Tenant/{houseId}")
async def create_tenant(houseId: int, request: CreateTenantSchema):
    tenant = Tenant(houseId=houseId, tenantPosition=0, **request.dict())
    monad = await repository.insert(tenant)
    if monad.error_status:
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return tenant.to_json()

@app.post("/Login")
async def login(request: LoginSchema):
    loginData = request.dict()
    tenant = Tenant(0, 0, password="")
    tenant.email = loginData["email"]
    tenant = await repository.get_tenant_by_email(tenant)
    if not tenant:
        return HTTPException(status_code="404", detail="Tenant not found")
    if not tenant.verify_password(loginData["password"], tenant.password):
        return HTTPException(status_code="401", detail="Invalid email or password")
    if tenant.houseId != loginData["houseId"]:
        return HTTPException(status_code="403", detail="Invalid house key")
    tenant.deviceId = loginData["deviceId"]
    monad = await repository.update(tenant)
    if monad.error_status:
        return HTTPException(status_code=monad.error_status["status"], detail=monad.error_status["reason"])
    return tenant.to_json()

    
    



  
@app.get("/House/{houseId}/Tenant")
async def get_tenants_by_house_id(houseId: int):
    tenant = Tenant(houseId=houseId, tenantPosition=0, password="")
    results = await repository.get_all(tenant)
    return [result.to_json() for result in results]


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8085)