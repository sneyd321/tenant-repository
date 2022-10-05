from models.db import DB
from models.repository import Repository
from models.redis import RedisHelper
from models.models import MaintenanceTicket
from models.directory import Directory
from pydantic.error_wrappers import ValidationError
from fastapi.responses import JSONResponse
from models.monad import ServiceDirectoryMaybeMonad, RedisMaybeMonad, RequestMaybeMonad

import pytest, asyncio, requests


def test_db_failed_to_connect():
    db = DB("root", "root", "localhost", "roomr")
    repository = Repository(db)
    maintenanceTicket = MaintenanceTicket(1)
    maintenanceTicket.id = 1
    async def do_test():
        monad = await repository.get(maintenanceTicket)
        assert monad.error_status == {"status": 502, "reason": "Failed to connect to database"}
    asyncio.run(do_test())
    

def test_redis_failed_to_connect():
    with open(r"tests/Capture.PNG", mode="rb") as image:
        redis = RedisHelper("localhost")
        monad = RedisMaybeMonad(f"MaintenanceTicket-1", image.read()).bind(redis.set_key)
        assert monad.error_status == {"status": 502, "reason": "Failed to connect to redis"}

def test_service_directory_connection():
    async def do_test():
        serviceDirectory = Directory(namespace="test")
        monad = await ServiceDirectoryMaybeMonad("scheduler").bind(serviceDirectory.resolve_service)
        assert monad.result == "172.17.0.1:8081"  
    asyncio.run(do_test())

def test_service_directory_invalid_namespace():
    async def do_test():
        serviceDirectory = Directory(namespace="afdsfsadfdsaf")
        monad = await ServiceDirectoryMaybeMonad("scheduler").bind(serviceDirectory.resolve_service)
        assert monad.error_status ==  {"status": 404, "reason": "Failed to resolve name"}
    asyncio.run(do_test())

def test_service_directory_invalid_name():
    async def do_test():
        serviceDirectory = Directory(namespace="test")
        monad = await ServiceDirectoryMaybeMonad("fdasfdsafdsaf").bind(serviceDirectory.resolve_service)
        assert monad.error_status ==  {"status": 404, "reason": "Failed to resolve name"}
    asyncio.run(do_test())

def test_failed_to_connect_to_scheduler():
    requestMonad = RequestMaybeMonad(f"http://localhost:8081/MaintenanceTicket/1", {"registration_token": "dsaffdsaffd"})
    requestMonad = requestMonad.bind(requests.post)
    assert requestMonad.error_status == {"status": 502, "reason": "Request failed to connect"}

