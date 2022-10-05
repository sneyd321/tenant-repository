
from sqlalchemy.exc import OperationalError, IntegrityError
from models.models import Tenant
from models.monad import RepositoryMaybeMonad
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Repository:

    def __init__(self, db):
        self.db = db


    async def create_all(self):
        async with self.db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await self.db.commit()
            

    async def insert(self, tenant):
        async with self.db.get_session():
            tenantPosition = await self.db.get_tenants_in_house(tenant.houseId)
            if tenantPosition > 0:
                tenantPosition -= 1
            tenant.tenantPosition = tenantPosition
            emails = await self.db.get_emails()
            
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.insert)
            if tenant.email in emails:
                return monad
                
            if monad.error_status:
                await self.db.rollback()
            else:
                await self.db.commit()
            return monad

    async def get_emails(self):
        async with self.db.get_session():
            return await self.db.get_emails()
        
                
    async def update(self, data):
        async with self.db.get_session():
            monad = await RepositoryMaybeMonad(data).bind(self.db.update)
            if monad.error_status:
                await self.db.rollback()
            else:
                await self.db.commit()
            return monad

    async def get(self, data):
        async with self.db.get_session():
            monad = await RepositoryMaybeMonad(data).bind(self.db.get)
            if monad.error_status:
                await self.db.rollback()
            else:
                await self.db.commit()
            return monad
            
            
    async def get_all(self, data):
        async with self.db.get_session():
            results = await self.db.get_by_house_id(data)
            if results:
                await self.db.commit()
            else:
                await self.db.rollback()
            return results

    async def get_tenant_by_email(self, data):
         async with self.db.get_session():
            results = await self.db.get_tenant_by_email(data)
            if results:
                await self.db.commit()
            else:
                await self.db.rollback()
            return results

    async def get_tenant_count_by_house(self, houseId):
        async with self.db.get_session():
            results = await self.db.get_tenants_in_house(houseId)
            if results:
                await self.db.commit()
            else:
                await self.db.rollback()
            return results