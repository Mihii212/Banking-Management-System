from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bank Management API is running"}

def test_create_account():
    # Create a new account
    data = {"owner_name": "Alice", "initial_deposit": 1000}
    response = client.post("/accounts", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["owner_name"] == "Alice"
    assert result["balance"] == 1000
    assert "id" in result

def test_list_accounts():
    # Create an account first
    data = {"owner_name": "Bob", "initial_deposit": 500}
    client.post("/accounts", json=data)

    # List accounts
    response = client.get("/accounts")
    assert response.status_code == 200
    accounts = response.json()
    assert isinstance(accounts, list)
    assert any(acc["owner_name"] == "Bob" for acc in accounts)

def test_transfer_success():
    # Create two accounts
    acc1 = client.post("/accounts", json={"owner_name": "Charlie", "initial_deposit": 1000}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Dave", "initial_deposit": 500}).json()

    # Transfer money
    transfer_data = {"from_account_id": acc1["id"], "to_account_id": acc2["id"], "amount": 300}
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["transferred"] == 300

def test_transfer_insufficient_funds():
    # Create two accounts
    acc1 = client.post("/accounts", json={"owner_name": "Eve", "initial_deposit": 100}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Frank", "initial_deposit": 200}).json()

    # Try to transfer more than balance
    transfer_data = {"from_account_id": acc1["id"], "to_account_id": acc2["id"], "amount": 500}
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]
