from collections.abc import Callable

from sqlalchemy.exc import OperationalError, IntegrityError
import redis, requests



class RepositoryMaybeMonad:

    def __init__(self, data, error_status = None):
        self.data = data
        self.error_status = error_status

    async def bind(self, function: Callable):
        if not self.data:
            self.error_status = {"status": 500, "reason": "No data in repository monad"}
            return RepositoryMaybeMonad(None, self.error_status)
        try:
            await function(self.data)
            
            return RepositoryMaybeMonad(self.data, error_status=self.error_status)
        except OperationalError:
            self.error_status = {"status": 502, "reason": "Failed to connect to database"}
            return RepositoryMaybeMonad(None, error_status=self.error_status)
        except IntegrityError:
            self.error_status = {"status": 409, "reason": "Failed to insert data into database"}
            return RepositoryMaybeMonad(None, error_status=self.error_status)

class ServiceDirectoryMaybeMonad:

    def __init__(self, data, result=None, error_status=None):
        self.data = data
        self.error_status = error_status
        self.result = result

    async def bind(self, function):
        if not self.data:
            self.error_status = {"status": 500, "reason": "No data in repository monad"}
            return ServiceDirectoryMaybeMonad(None, None, self.error_status)
        try:
            self.result = await function(self.data)
            return ServiceDirectoryMaybeMonad(None, self.result, self.error_status)
        except ServiceUnavailable:
            self.error_status = {"status": 502, "reason": "Failed to connect to service directory"}
            return ServiceDirectoryMaybeMonad(None, None, self.error_status)
        except NotFound:
            self.error_status = {"status": 404, "reason": "Failed to resolve name"}
            return ServiceDirectoryMaybeMonad(None, None, self.error_status)

