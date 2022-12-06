from firebase_admin import credentials, storage
import firebase_admin, base64
from firebase_admin import firestore

class Firebase:


    def __init__(self):  
        self._serviceAccountPath = r'./static/ServiceAccount.json'
    
    def setServiceAccountPath(self, path):
        self._serviceAccountPath = path

    def init_app(self):
        cred = credentials.Certificate(self._serviceAccountPath)
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate(self._serviceAccountPath)
            firebase_admin.initialize_app(cred, {'storageBucket' : 'roomr-222721.appspot.com'})
        self._db = firestore.client()

    def create_blob_no_cache(self, filePath):
        bucket = storage.bucket()
        blob = bucket.blob(filePath)
        blob.cache_control = "no-cache"
        return blob
       



