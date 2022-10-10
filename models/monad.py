from collections.abc import Callable
from sqlalchemy.exc import OperationalError, IntegrityError

class RepositoryMaybeMonad:
    def __init__(self, data, error_status = None):
        self.data = data
        self.error_status = error_status

    def has_errors(self):
        return self.error_status != None

    async def bind(self, function: Callable):
        if self.data == None:
            if self.error_status == None:
                self.error_status = {"status": 404, "reason": "No data in repository monad"}
                return RepositoryMaybeMonad(data=None, error_status=self.error_status)
            return RepositoryMaybeMonad(data=None, error_status=self.error_status)
        try:
            await function(self.data)
            return RepositoryMaybeMonad(data=self.data, error_status=self.error_status)
        except OperationalError:
            self.error_status = {"status": 502, "reason": "Failed to connect to database"}
            return RepositoryMaybeMonad(None, error_status=self.error_status)
        except IntegrityError:
            self.error_status = {"status": 409, "reason": "Failed to insert data into database"}
            return RepositoryMaybeMonad(None, error_status=self.error_status)

    async def bind_data(self, function: Callable):
        if self.data == None:
            return RepositoryMaybeMonad(data=None, error_status=self.error_status)
        try:
            result = await function(self.data)
            if result == None:
                self.error_status = {"status": 404, "reason": "No data"}
                return RepositoryMaybeMonad(data=None, error_status=self.error_status)
            return RepositoryMaybeMonad(data=result, error_status=self.error_status)
        except OperationalError:
            self.error_status = {"status": 502, "reason": "Failed to connect to database"}
            return RepositoryMaybeMonad(None, error_status=self.error_status)
        except IntegrityError:
            self.error_status = {"status": 409, "reason": "Failed to insert data into database"}
            return RepositoryMaybeMonad(None, error_status=self.error_status)
