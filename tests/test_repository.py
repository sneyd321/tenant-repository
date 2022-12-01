from models.db import DB
from models.repository import Repository
from models.models import Tenant
import pytest, asyncio, json, os, time

async def test_Tenant_Service_will_return_error_if_account_with_same_email_exists():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open(r"./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
    monad = await repository.insert_temp(tenant)
    monad = await repository.insert_temp(tenant)
    assert monad.error_status == {"status": 409, "reason": "Tenant email already exists"}

async def test_Tenant_Service_will_update_lease_position_when_greater_than_0():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open(r"./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
    tenant = await repository.set_tenant_lease_position(2, tenant)
    assert tenant.tenantPosition == 1

async def test_Tenant_Service_will_update_lease_position_when_equal_to_0():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open(r"./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
    tenant = await repository.set_tenant_lease_position(0, tenant)
    assert tenant.tenantPosition == 0


async def test_Tenant_Service_will_return_error_account_does_not_exist_on_update_state():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.email = "asfdasfa3rt42qtra"
    monad = await repository.update_tenant(tenant, "Approved")
    assert monad.error_status == {"status": 404, "reason": f"Tenant not found with email: ${tenant.email}"}

async def test_Tenant_Service_returns_an_error_message_when_account_does_not_exist():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.email = "ZQAFDSAF@DFSAFDASF.com"
    monad = await repository.login(tenant, "aaaaaa")
    assert monad.error_status == {"status": 404, "reason": "Invalid email or password"}


async def test_Tenant_Service_returns_an_error_message_with_invalid_house_id():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.houseId = -1
    monad = await repository.login(tenant, "aaaaaa")
    assert monad.error_status == {"status": 403, "reason": "Invalid house key"}

   
async def test_Tenant_Service_returns_an_error_message_when_password_is_invalid():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
    monad = await repository.login(tenant, "bbbbbb")
    assert monad.error_status == {"status": 401, "reason": "Invalid email or password"}

async def test_Tenant_Service_will_return_error_on_login_if_in_invite_pending_state():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.tenantState = "PendingInvite"
    monad = await repository.login(tenant, "aaaaaa")
    assert monad.error_status == {"status": 403, "reason": "Not Approved. Please check email for an email to activate you account."}


async def test_Tenant_Service_will_return_error_on_login_if_in_temp_account_created_state():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.tenantState = "TempAccountCreated"
    monad = await repository.login(tenant, "aaaaaa")
    assert monad.error_status == {"status": 403, "reason": "Not Approved. Please message landlord to invite you."}


async def test_Tenant_Service_will_return_error_on_login_if_in_invalid_state():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.tenantState = "BAD_STATE!!@E#@!#"
    monad = await repository.login(tenant, "aaaaaa")
    assert monad.error_status == {"status": 403, "reason": "Not Approved. Tenant in invalid state."}


async def test_Tenant_Service_returns_an_empty_list_when_retrieving_a_list_of_zero_items():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.houseId = -1
    monad = await repository.get_tenants_by_house_id(tenant)
    assert monad.get_param_at(0) == []

async def Tenant_Service_returns_error_when_account_does_not_exist_on_delete():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    with open("./tests/sample_tenant.json", mode="r") as sample_tenant:
        tenantData = json.load(sample_tenant)
        tenant = Tenant(**tenantData)
        tenant.email = "ZQAFDSAF@DFSAFDASF.com"
    monad = await repository.delete(tenant)
    assert monad.error_status == {"status": 404, "reason": f"Tenant not found with email: {tenant.email}"}