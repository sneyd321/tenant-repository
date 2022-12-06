import json, os

with open("./models/static/ServiceAccount.json") as serviceAccount:
    key = json.load(serviceAccount)

os.system(f"gcloud iam service-accounts keys delete {key['private_key_id']} --iam-account=firebase-adminsdk-rbs1y@roomr-222721.iam.gserviceaccount.com --quiet")  

