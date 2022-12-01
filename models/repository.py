from models.monad import RepositoryMaybeMonad


class Repository:

    def __init__(self, db):
        self.db = db

    async def set_tenant_lease_position(self, tenantCount, tenant):
        if tenantCount != 0:
            tenantCount -= 1 
        tenant.tenantPosition = tenantCount
        return tenant

    async def insert_temp(self, tenant):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)

            if tenantFromDB is not None:
                return RepositoryMaybeMonad(None, error_status={"status": 409, "reason": "Tenant email already exists"})
            
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.insert)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            await RepositoryMaybeMonad().bind(self.db.commit)
            await session.close()
            return monad
           

    async def update_tenant(self, tenant, tenantState):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": f"Tenant not found with email: ${tenant.email}"})

            tenant.houseId = tenantFromDB.houseId
            tenant.tenantState = tenantState
            tenant.id = tenantFromDB.id

            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.count_tenants_in_house)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            tenant = await self.set_tenant_lease_position(monad.get_param_at(0), tenant)
       
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.update)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad

            await RepositoryMaybeMonad().bind(self.db.commit)
            await session.close()
            return monad
           

    async def login(self, tenant, password):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": "Invalid email or password"})
    
            if not tenant.verify_password(password, tenantFromDB.password):
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})

            if tenant.houseId != tenantFromDB.houseId:
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Invalid house key"})
            
            if tenant.tenantState == "TempAccountCreated":
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Not Approved. Please message landlord to invite you."})

            if tenant.tenantState == "PendingInvite":
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Not Approved. Please check email for an email to activate you account."})

            if tenant.tenantState != "Approved":
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Not Approved. Tenant in invalid state."})
            
            tenantFromDB.deviceId = tenant.deviceId
            monad = await RepositoryMaybeMonad(tenantFromDB).bind(self.db.update)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad

            await RepositoryMaybeMonad().bind(self.db.commit)
            await session.close()
            return monad
        

    async def get_tenants_by_house_id(self, tenant):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.get_by_house_id)
            await session.close()
            return monad
    

    async def delete_tenant(self, tenant):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": f"Tenant not found with email: {tenant.email}"})
            
            monad = await RepositoryMaybeMonad(tenantFromDB).bind(self.db.delete_by_email)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            await RepositoryMaybeMonad().bind(self.db.commit)
            await session.close()
            return monad
