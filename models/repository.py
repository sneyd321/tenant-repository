from models.monad import RepositoryMaybeMonad


class Repository:

    def __init__(self, db):
        self.db = db

    async def commit(self, tenant):
        await self.db.commit()

    async def rollback(self, tenant):
        await self.db.rollback()

    async def calculate_tenant_position(self, tenantCount):
        if tenantCount > 0:
            tenantCount -= 1
        return tenantCount

    async def insert(self, tenant):
        async with self.db.get_session():
            # Count tenants with same houseId
            monad = RepositoryMaybeMonad(tenant)
            monad = await monad.bind_data(self.db.count_tenants_in_house)
            monad = await monad.bind_data(self.calculate_tenant_position)
            # Update tenant with position it will appear in lease agreement
            if monad.data is not None:
                tenant.tenantPosition = monad.data
                monad.data = tenant
            monad = await monad.bind(self.db.insert)
            monad = await monad.bind(self.commit)
            return monad

    async def login(self, tenant, password):
        async with self.db.get_session():
            monad = RepositoryMaybeMonad(tenant)
            monad = await monad.bind_data(self.db.get_tenant_by_email)
            # Check if tenant exists
            if monad.data is None:
                return monad
            
            # Check if password matches
            if not tenant.verify_password(password, monad.data.password):
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})
            
            #Check if house id is valid
            if tenant.houseId != monad.data.houseId:
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Invalid house key"})
            
            #Update deviceId recieved in loginData
            monad = await monad.bind(self.db.update)
            monad = await monad.bind(self.commit)
            return monad

    async def get_tenants_by_house_id(self, tenant):
        async with self.db.get_session():
            monad = RepositoryMaybeMonad(tenant)
            monad = await monad.bind_data(self.db.get_by_house_id)
            return monad
            