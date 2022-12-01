from main import app
import requests

def test_Tenant_Service_health_check_returns_successfully():
    response = requests.get("http://localhost:8085/Health")
    assert response.status_code == 200
 
def test_Tenant_Service_Login_returns_successfully_if_in_approved_state():
   
    response = requests.post("http://localhost:8085/Login",json={
            "email": "a@s.com",
            "password": "aaaaaa",
            "houseId": 2,
            "deviceId": ""
        })
        
    assert response.status_code == 200
   


def test_Tenant_Service_update_tenant_state_returns_successfully():
    response = requests.put("http://localhost:8085/Tenant/Approved", json={
            "firstName": "Test",
            "lastName": "test",
            "email": "a@s.com",
            "password": ""
        })
    assert response.status_code == 200
    
    
   


def test_Tenant_Service_get_all_tenants_by_house_id_returns_successfully():
    response = requests.get("http://localhost:8085/House/1/Tenant")
    assert response.status_code == 200




def test_Tenant_Service_delete_returns_successfully():
    response = requests.delete("http://localhost:8085/Tenant", headers={}, json={
        "email": "a@s.com",
        "password": "aaaaaa",
        "firstName": "",
        "lastName": "",
        "tenantState": "Approved"
    })
    assert response.status_code == 200

