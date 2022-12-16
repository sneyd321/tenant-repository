from models.monad import RepositoryMaybeMonad


class Repository:


    def __init__(self, db):
        self.db = db


    async def set_tenant_lease_position(self, tenantCount, tenant):
        if tenantCount != 0:
            tenantCount -= 1 
        tenant.tenantPosition = tenantCount
        return tenant


    async def insert_temp(self, tenant, firebase, isTest):
        async with self.db.get_session() as session:
            #Get Tenant to check if it exists
            monad = await RepositoryMaybeMonad(tenant.email).bind_data(self.db.get_tenant_by_email)
            if monad.has_errors():
                return monad
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is not None:
                return RepositoryMaybeMonad(None, error_status={"status": 409, "reason": "Tenant email already exists"})
            #Insert Tenant
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.insert)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            await RepositoryMaybeMonad().bind(self.db.commit)
            #Don't add test data to prod folder
            if isTest:
                tenant.setProfileURL(firebase, f"Test/Tenant_{tenant.id}.jpg")
            else:
                tenant.setProfileURL(firebase, f"Profiles/Tenant/Tenant_{tenant.id}.jpg")
            #Update Profile
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.update_profile_url)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            await RepositoryMaybeMonad().bind(self.db.commit)
            return monad

    
           


    async def update_tenant_state(self, tenant, state):
        async with self.db.get_session() as session:
            #Get Tenant to check is it exists
            monad = await RepositoryMaybeMonad(tenant.email).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": f"Tenant not found with email: ${tenant.email}"})
            #Update tenant 
            tenant.id = tenantFromDB.id
            tenant.state = state
            tenant.houseId = tenantFromDB.houseId
            tenant.profileURL = tenantFromDB.profileURL
         
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.update_state)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
           
            await RepositoryMaybeMonad().bind(self.db.commit)
            return monad
           


    async def login(self, email, password, houseId, deviceId):
        async with self.db.get_session() as session:
            #Check if Tenant exists 
            monad = await RepositoryMaybeMonad(email).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": "Invalid email or password"})
            #Is password valid?
            if not tenantFromDB.verify_password(password, tenantFromDB.password):
                return RepositoryMaybeMonad(None, error_status={"status": 401, "reason": "Invalid email or password"})
            #Is correct houseId?
            if houseId != tenantFromDB.houseId:
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Invalid house key"})
            #Is in valid state?
            if tenantFromDB.state == "TempAccountCreated":
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Not Approved. Please message landlord to invite you."})
            if tenantFromDB.state == "PendingInvite":
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Not Approved. Please check email for an email to activate you account."})
            if tenantFromDB.state != "Approved":
                return RepositoryMaybeMonad(None, error_status={"status": 403, "reason": "Not Approved. Tenant in invalid state."})
            
            #Update device id
            tenantFromDB.deviceId = deviceId
            monad = await RepositoryMaybeMonad(tenantFromDB).bind(self.db.update_device_id)

            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            await RepositoryMaybeMonad().bind(self.db.commit)
            return monad
        


    async def get_tenants_by_house_id(self, tenant):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant).bind_data(self.db.get_by_house_id)
            return monad
    


    async def delete_tenant(self, tenant):
        async with self.db.get_session() as session:
            
            monad = await RepositoryMaybeMonad(tenant.email).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": f"Tenant not found with email: {tenant.email}"})
            
            monad = await RepositoryMaybeMonad(tenantFromDB).bind(self.db.delete_by_email)
            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad

            await RepositoryMaybeMonad().bind(self.db.commit)
            return monad



    async def update_tenant(self, tenant):
        async with self.db.get_session() as session:
            monad = await RepositoryMaybeMonad(tenant.email).bind_data(self.db.get_tenant_by_email)
            tenantFromDB = monad.get_param_at(0)
            if tenantFromDB is None:
                return RepositoryMaybeMonad(None, error_status={"status": 404, "reason": f"Tenant not found with email: {tenant.email}"})

            tenant.id = tenantFromDB.id
            tenant.houseId = tenantFromDB.houseId
            monad = await RepositoryMaybeMonad(tenant).bind(self.db.update)

            if monad.has_errors():
                await RepositoryMaybeMonad().bind(self.db.rollback)
                return monad
            await RepositoryMaybeMonad().bind(self.db.commit)
            return monad