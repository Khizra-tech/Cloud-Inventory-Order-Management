from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

import pyodbc

app = FastAPI(
    title="Cloud Inventory and Order Management API",
    description="API for managing inventory and customer orders",
    version="1.0.0"
)

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)

class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)

class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    items: List[OrderItemCreate] = Field(min_length=1)

class OrderStatusUpdate(BaseModel):
    status: str = Field(
        min_length=1,
        max_length=30
    )

def get_connection():
    connection_string = (
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=localhost\SQLEXPRESS;"
        r"DATABASE=CloudInventoryDB;"
        r"Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)


@app.get("/")
def home():
    return {
        "message": "Cloud Inventory API is running!",
        "status": "success"
    }


@app.get("/products")
def get_products():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT ProductID, NAME, price, quantity, recorderlevel
                FROM dbo.Products
                ORDER BY ProductID
            """)

            rows = cursor.fetchall()

            return [
                {
                    "product_id": row[0],
                    "name": row[1],
                    "price": float(row[2]),
                    "quantity": row[3],
                    "reorder_level": row[4]
                }
                for row in rows
            ]

    except pyodbc.Error as error:
        print("Database error in GET /products:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve products from the database."
        ) from error
@app.get("/products/{product_id}")
def get_product(product_id: int):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT ProductID, NAME, price, quantity, recorderlevel
                FROM dbo.Products
                WHERE ProductID = ?
            """, (product_id,))

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            return {
                "product_id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "quantity": row[3],
                "reorder_level": row[4]
            }

    except pyodbc.Error as error:
        print("Database error in GET /products/{product_id}:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve the product."
        ) from error

@app.get("/products/low-stock")
def get_low_stock_products():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT ProductID, NAME, price, quantity, recorderlevel
                FROM dbo.Products
                WHERE quantity <= recorderlevel
                ORDER BY quantity ASC
            """)

            rows = cursor.fetchall()

            return [
                {
                    "product_id": row[0],
                    "name": row[1],
                    "price": float(row[2]),
                    "quantity": row[3],
                    "reorder_level": row[4]
                }
                for row in rows
            ]

    except pyodbc.Error as error:
        print("Database error in GET /products/low-stock:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve low-stock products."
        ) from error

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO dbo.Products
                    (NAME, price, quantity, recorderlevel)
                OUTPUT
                    INSERTED.ProductID,
                    INSERTED.NAME,
                    INSERTED.price,
                    INSERTED.quantity,
                    INSERTED.recorderlevel
                VALUES (?, ?, ?, ?)
            """, (
                product.name,
                product.price,
                product.quantity,
                product.reorder_level
            ))

            row = cursor.fetchone()
            connection.commit()

            return {
                "product_id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "quantity": row[3],
                "reorder_level": row[4]
            }

    except pyodbc.Error as error:
        print("Database error in POST /products:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not create the product."
        ) from error

@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE dbo.Products
                SET NAME = ?,
                    price = ?,
                    quantity = ?,
                    recorderlevel = ?
                WHERE ProductID = ?
            """, (
                product.name,
                product.price,
                product.quantity,
                product.reorder_level,
                product_id
            ))

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            connection.commit()

            cursor.execute("""
                SELECT ProductID, NAME, price, quantity, recorderlevel
                FROM dbo.Products
                WHERE ProductID = ?
            """, (product_id,))

            row = cursor.fetchone()

            return {
                "product_id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "quantity": row[3],
                "reorder_level": row[4]
            }

    except pyodbc.Error as error:
        print("Database error in PUT /products/{product_id}:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not update the product."
        ) from error

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM dbo.Products
                WHERE ProductID = ?
            """, (product_id,))

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            connection.commit()

            return {
                "message": "Product deleted successfully",
                "product_id": product_id
            }

    except pyodbc.Error as error:
        print("Database error in DELETE /products/{product_id}:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not delete the product."
        ) from error

@app.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    # Reject duplicate products in the same order.
    product_ids = [item.product_id for item in order.items]

    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            status_code=400,
            detail="Each product can appear only once in an order."
        )

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check that every product exists and has enough stock.
        product_details = []

        for item in order.items:
            cursor.execute("""
                SELECT ProductID, NAME, price, quantity
                FROM dbo.Products
                WHERE ProductID = ?
            """, (item.product_id,))

            product = cursor.fetchone()

            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product ID {item.product_id} was not found."
                )

            if product[3] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Not enough stock for {product[1]}. "
                        f"Available quantity: {product[3]}."
                    )
                )

            product_details.append({
                "product_id": product[0],
                "name": product[1],
                "unit_price": float(product[2]),
                "quantity": item.quantity
            })

        # Create the order.
        cursor.execute("""
            INSERT INTO dbo.Orders (CustomerName, OrderDate, status)
            OUTPUT INSERTED.OrderID
            VALUES (?, SYSDATETIME(), ?)
        """, (order.customer_name.strip(), "Pending"))

        order_id = cursor.fetchone()[0]

        # Add order items and deduct stock safely.
        for item, product in zip(order.items, product_details):
            cursor.execute("""
                UPDATE dbo.Products
                SET quantity = quantity - ?
                WHERE ProductID = ?
                  AND quantity >= ?
            """, (
                item.quantity,
                item.product_id,
                item.quantity
            ))

            if cursor.rowcount != 1:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Stock changed while processing "
                        f"{product['name']}. Please try again."
                    )
                )

            cursor.execute("""
                INSERT INTO dbo.OrderItems
                    (OrderID, ProductID, quantity, unitprice)
                VALUES (?, ?, ?, ?)
            """, (
                order_id,
                item.product_id,
                item.quantity,
                product["unit_price"]
            ))

        # Commit the order and stock changes together.
        connection.commit()

        total_amount = sum(
            product["unit_price"] * product["quantity"]
            for product in product_details
        )

        return {
            "message": "Order created successfully.",
            "order_id": order_id,
            "customer_name": order.customer_name.strip(),
            "status": "Pending",
            "items": product_details,
            "total_amount": round(total_amount, 2)
        }

    except HTTPException:
        if connection is not None:
            connection.rollback()
        raise

    except Exception as error:
        if connection is not None:
            connection.rollback()

        print("Database error in POST /orders:", error)

        raise HTTPException(
            status_code=500,
            detail="Could not create the order."
        ) from error

    finally:
        if connection is not None:
            connection.close()

@app.get("/orders")
def get_orders():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    o.OrderID,
                    o.CustomerName,
                    o.OrderDate,
                    o.status,
                    COALESCE(
                        SUM(oi.quantity * oi.unitprice),
                        0
                    ) AS total_amount
                FROM dbo.Orders AS o
                LEFT JOIN dbo.OrderItems AS oi
                    ON o.OrderID = oi.OrderID
                GROUP BY
                    o.OrderID,
                    o.CustomerName,
                    o.OrderDate,
                    o.status
                ORDER BY o.OrderID DESC
            """)

            rows = cursor.fetchall()

            return [
                {
                    "order_id": row[0],
                    "customer_name": row[1],
                    "order_date": (
                        row[2].isoformat() if row[2] else None
                    ),
                    "status": row[3],
                    "total_amount": float(row[4])
                }
                for row in rows
            ]

    except Exception as error:
        print("Database error in GET /orders:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve orders."
        ) from error

@app.get("/orders/{order_id}")
def get_order_details(order_id: int):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            # Get the order information.
            cursor.execute("""
                SELECT OrderID, CustomerName, OrderDate, status
                FROM dbo.Orders
                WHERE OrderID = ?
            """, (order_id,))

            order = cursor.fetchone()

            if order is None:
                raise HTTPException(
                    status_code=404,
                    detail="Order not found."
                )

            # Get the products included in this order.
            cursor.execute("""
                SELECT
                    oi.ProductID,
                    p.NAME,
                    oi.quantity,
                    oi.unitprice
                FROM dbo.OrderItems AS oi
                LEFT JOIN dbo.Products AS p
                    ON oi.ProductID = p.ProductID
                WHERE oi.OrderID = ?
                ORDER BY oi.OrderItemId
            """, (order_id,))

            rows = cursor.fetchall()

            items = [
                {
                    "product_id": row[0],
                    "product_name": row[1],
                    "quantity": row[2],
                    "unit_price": float(row[3]),
                    "subtotal": round(
                        row[2] * float(row[3]), 2
                    )
                }
                for row in rows
            ]

            total_amount = sum(
                item["subtotal"] for item in items
            )

            return {
                "order_id": order[0],
                "customer_name": order[1],
                "order_date": (
                    order[2].isoformat() if order[2] else None
                ),
                "status": order[3],
                "items": items,
                "total_amount": round(total_amount, 2)
            }

    except HTTPException:
        raise

    except Exception as error:
        print("Database error in GET /orders/{order_id}:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve order details."
        ) from error

@app.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate
):
    allowed_statuses = {
        "Pending",
        "Processing",
        "Shipped",
        "Completed",
        "Cancelled"
    }

    new_status = update.status.strip().title()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Choose Pending, Processing, "
                "Shipped, Completed, or Cancelled."
            )
        )

    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE dbo.Orders
                SET status = ?
                WHERE OrderID = ?
            """, (new_status, order_id))

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Order not found."
                )

            connection.commit()

            return {
                "message": "Order status updated successfully.",
                "order_id": order_id,
                "status": new_status
            }

    except HTTPException:
        raise

    except Exception as error:
        print("Database error updating order status:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not update order status."
        ) from error

@app.get("/inventory/summary")
def get_inventory_summary():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_products,
                    COALESCE(SUM(quantity), 0) AS total_units,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN quantity <= recorderlevel
                                THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    ) AS low_stock_products,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN quantity < recorderlevel
                                THEN (recorderlevel - quantity) * price
                                ELSE 0
                            END
                        ),
                        0
                    ) AS estimated_restock_cost
                FROM dbo.Products
            """)

            row = cursor.fetchone()

            return {
                "total_products": row[0],
                "total_units_in_stock": row[1],
                "low_stock_products": row[2],
                "estimated_restock_cost": round(
                    float(row[3]), 2
                )
            }

    except Exception as error:
        print("Database error in inventory summary:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve inventory summary."
        ) from error
        