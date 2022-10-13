from models.monad import RepositoryMaybeMonad


class Repository:

    def __init__(self, db):
        self.db = db

    async def calculate_tenant_lease_position(self, tenantCount, tenant):
        if tenantCount > 0:
            tenantCount -= 1 
        tenant.tenantPosition = tenantCount
        return tenant

    async def insert(self, tenant):
        async with self.db.get_session():
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_tenant_by_email)
            if monad.get_param_at(0):
                return RepositoryMaybeMonad(error_status={"status": 409, "reason": "Failed to insert data into database"})
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.count_tenants_in_house)
            monad = await RepositoryMaybeMonad(monad.get_param_at(0), tenant) \
                .bind_data(self.calculate_tenant_lease_position)
            await RepositoryMaybeMonad(monad.get_param_at(0)) \
                .bind(self.db.insert)
            return await RepositoryMaybeMonad() \
                .bind(self.db.commit)
           

    async def login(self, tenant, password):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})
    
            if not tenant.verify_password(password, tenantFromDB.password):
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})

            if tenant.houseId != tenantFromDB.houseId:
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Invalid house key"})
            
            await RepositoryMaybeMonad(tenant) \
                .bind(self.db.update)

            return await RepositoryMaybeMonad(tenant) \
                .bind(self.commit)
        

    async def get_tenants_by_house_id(self, tenant):
        async with self.db.get_session():
            return await RepositoryMaybeMonad(tenant) \
                .bind_data(self.db.get_by_house_id)
    
