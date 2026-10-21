# Database Data Model

## 1. Products Table

Purpose: Store product and inventory information.

Primary key: productId (Partition Key)

Fields:
- productId: Unique product identifier
- name: Product name
- price: Product price
- quantity: Available stock
- reorderLevel: Minimum stock threshold
- category: Product category

Example record:

```json
{
  "productId": "P001",
  "name": "Wireless Mouse",
  "price": 2500,
  "quantity": 12,
  "reorderLevel": 5,
  "category": "Electronics"
}
```

## 2. Orders Table

Purpose: Store customer orders.

Primary key: orderId (Partition Key)

Fields:
- orderId: Unique order identifier
- customerName: Fictional customer name
- items: List of ordered products and quantities
- totalAmount: Total order value
- status: Order status

Example record:

```json
{
  "orderId": "O001",
  "customerName": "Example Customer",
  "items": [
    {
      "productId": "P001",
      "quantity": 2
    }
  ],
  "totalAmount": 5000,
  "status": "Pending"
}
```

## 3. Business Rules

- Product IDs and order IDs must be unique.
- Product quantity cannot be negative.
- A product is low in stock when quantity is less than or equal to its reorderLevel.
- An order must contain at least one item.
- Customer names and records in this project are fictional.
-
