from models.db import DB
from models.repository import Repository
from models.models import Tenant
import asyncio

@pytest.mark.asyncio
def test_Tenant_Service_returns_an_error_message_unable_to_connect_to_database():
    db = DB("test", "homeowner", "localhost", "roomr")
    repository = Repository(db)
    async def do_test():
        monad = await repository.insert(Tenant("aaaaaa"))
        assert monad.error_status == {"status": 502, "reason": "Failed to connect to database"}
    asyncio.run(do_test())

