from models.db import DB
from models.repository import Repository
from models.models import Tenant
import asyncio, pytest

@pytest.mark.asyncio
async def test_Tenant_Service_returns_an_error_message_unable_to_connect_to_database():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    monad = await repository.insert_temp(Tenant("aaaaaa"))
    assert monad.error_status == {"status": 502, "reason": "Failed to connect to database"}

