
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

Base = declarative_base()


class Tenant(Base):
    __tablename__ = 'tenant'

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    id = Column(Integer(), primary_key=True)
    houseId = Column(Integer(), nullable=False)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phoneNumber = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    state = Column(String(30), nullable=False)
    deviceId = Column(String(180), nullable=True)
    profileURL = Column(String(223), nullable=True)

    def __init__(self, **kwargs):
        self.houseId = kwargs.get("houseId")
        self.firstName = kwargs.get("firstName")
        self.lastName = kwargs.get("lastName")
        self.email = kwargs.get("email")
        self.password = kwargs.get("password")
        self.phoneNumber = kwargs.get("phoneNumber")
        self.state = "Temp_Account_Created"
        self.deviceId = kwargs.get("deviceId", "")
        self.profileURL = kwargs.get("profileURL")

    def set_state(self):
        return {
            "state": self.state
        }

    def setProfileURL(self, firebase, bucketPath):
        blob = firebase.create_blob_no_cache(bucketPath)
        blob.upload_from_string(b"", content_type="image/jpg")
        self.profileURL = blob.public_url

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def to_json(self):
        return {
            "houseId": self.houseId,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "phoneNumber": self.phoneNumber,
            "state": self.state,
            "deviceId": self.deviceId,
            "profileURL": self.profileURL
        }

    def update_profile_url(self):
        return {
            "profileURL": self.profileURL
        }
    

    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "phoneNumber": self.phoneNumber,
            "password": self.get_password_hash(self.password),
        }
    
    def update_device_id(self):
        return {
            "deviceId": self.deviceId,
        }

