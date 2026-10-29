from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_inventory_summary():
    response = client.get("/inventory/summary")
    assert response.status_code == 200

    data = response.json()
    assert "total_products" in data
    assert "total_units_in_stock" in data
    assert "low_stock_products" in data
    assert "estimated_restock_cost" in data


def test_invalid_product_id():
    response = client.get("/products/999999999")
    assert response.status_code == 404