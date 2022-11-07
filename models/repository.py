from models.monad import RepositoryMaybeMonad


class Repository:

    def __init__(self, db):
        self.db = db

    async def set_tenant_lease_position(self, tenantCount, tenant):
        if tenantCount > 0:
            tenantCount -= 1 
        tenant.tenantPosition = tenantCount
        return tenant

    async def insert_temp(self, tenant):
        async with self.db.get_session():
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_tenant_by_email)
            if monad.get_param_at(0) is not None:
                return RepositoryMaybeMonad(None, error_status={"status": 409, "reason": "Failed to insert data into database"})
            monad = await RepositoryMaybeMonad(tenant) \
                .bind(self.db.insert)
            await RepositoryMaybeMonad() \
                .bind(self.db.commit)
            return monad
           

    async def login(self, tenant, password):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_tenant_by_email)
    
            if monad.get_param_at(0) is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": "Invalid email or password"})
    
            if not tenant.verify_password(password, monad.get_param_at(0).password):
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})

            if tenant.houseId != monad.get_param_at(0).houseId:
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Invalid house key"})
            
            await RepositoryMaybeMonad(tenant) \
                .bind(self.db.update)

            await RepositoryMaybeMonad() \
                .bind(self.db.commit)

            return monad

    async def update_tenant(self, tenant, tenantState):
        async with self.db.get_session():
            #Get Tenant From DB
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": "Invalid email or password"})

            #Set Tenant Fields
            tenant.houseId = tenantFromDB.houseId
            tenant.tenantState = tenantState
            
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.count_tenants_in_house)
            if monad.has_errors():
                return monad
            tenantPosition = monad.get_param_at(0)
            if tenantPosition > 0:
                tenantPosition -= 1 
            tenant.tenantPosition = tenantPosition
       
             
            monad = await RepositoryMaybeMonad(tenant) \
                .bind(self.db.update)
            if monad.has_errors():
                return monad

            await RepositoryMaybeMonad() \
                .bind(self.db.commit)

            return monad
           

    async def login(self, tenant, password):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_tenant_by_email)
    
            if monad.get_param_at(0) is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": "Invalid email or password"})
    
            if not tenant.verify_password(password, monad.get_param_at(0).password):
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})

            if tenant.houseId != monad.get_param_at(0).houseId:
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Invalid house key"})
            
            await RepositoryMaybeMonad(tenant) \
                .bind(self.db.update)

            await RepositoryMaybeMonad() \
                .bind(self.db.commit)

            return monad
        

    async def get_tenants_by_house_id(self, tenant):
        async with self.db.get_session():
            return await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_by_house_id)
    
