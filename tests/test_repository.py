from models.db import DB
from models.repository import Repository
from models.models import Tenant
import pytest, asyncio, json, os, time


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_Tenant_Service_returns_an_error_message_conflict_in_database_when_an_integrity_error_occurs():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open(r"./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        print(tenantData)
        tenant = Tenant(**tenantData)
      
    monad = await repository.insert(tenant)
    time.sleep(60)
    monad = await repository.insert(tenant)

    assert monad.error_status == {"status": 409, "reason": "Failed to insert data into database"}
   
@pytest.mark.asyncio
async def test_Tenant_Service_returns_an_empty_list_when_retrieving_a_list_of_zero_items():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.houseId = -1
    monad = await repository.get_tenants_by_house_id(tenant)
    assert monad.data == []

@pytest.mark.asyncio
async def test_Tenant_Service_returns_an_error_message_when_account_does_not_exist():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.email = "ZQAFDSAF@DFSAFDASF.com"
    monad = await repository.login(tenant, "aaaaaa")
 
    assert monad.error_status == {"status": 404, "reason": "No data"}

@pytest.mark.asyncio
async def test_Tenant_Service_returns_an_error_message_when_password_is_invalid():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
    monad = await repository.login(tenant, "bbbbbb")
    assert monad.error_status == {"status": 401, "reason": "Invalid email or password"}


@pytest.mark.asyncio
async def test_Tenant_Service_returns_an_error_message_with_invalid_house_id():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.houseId = -1
    monad = await repository.login(tenant, "aaaaaa")
    assert monad.error_status == {"status": 403, "reason": "Invalid house key"}
