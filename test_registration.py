import requests
import json

# Test registration endpoint
def test_registration():
    url = "http://localhost:8000/api/accounts/register/"
    
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone_number": "+254700000000",
        "date_of_birth": "1990-01-01",
        "password": "TestPassword123",
        "password_confirm": "TestPassword123"
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("Registration successful!")
        else:
            print("Registration failed!")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration()
