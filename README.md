# Cloud-Based Inventory and Order Management System

A backend API project for managing product inventory, tracking stock levels, and processing customer orders using FastAPI and Microsoft SQL Server.

## Features

- Retrieve all products
- Retrieve a product by ID
- Create, update, and delete products
- Identify low-stock products
- Create customer orders
- View all orders and individual order details
- Update order statuses
- Generate an inventory summary
- Validate requests and handle errors
- Automated API tests using pytest

## Technology Stack

- Python 3.12
- FastAPI
- Pydantic
- Microsoft SQL Server Express
- pyodbc
- Uvicorn
- pytest

## Project Structure

```text
Cloud-Inventory-Order-Management/
├── src/
│   ├── main.py
│   ├── test_api.py
│   └── requirements.txt
|   └── test_connection.py
└── data-model.md
└── README.md
└── CloudInventoryDB.sql


## Local Setup

### 1. Prerequisites

Install Python 3.12, Microsoft SQL Server Express, SQL Server Management Studio, and Microsoft ODBC Driver 17 for SQL Server.

### 2. Create the database

Create a SQL Server database named `CloudInventoryDB`.

Create the required `Products`, `Orders`, and `OrderItems` tables using the SQL scripts provided in the project documentation.

Ensure that the table and column names match the application code.

### 3. Install dependencies

Open a terminal in the `src` folder and run:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the database connection

The current development configuration uses Windows Authentication with a local SQL Server Express instance.

Review the connection settings in `src/main.py` and update the server name if your local SQL Server instance differs.

Do not commit passwords, credentials, or other secrets to GitHub.

### 5. Start the API

From the `src` folder, run:

```bash
python -m uvicorn main:app --reload
```

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

## Run Automated Tests

From the `src` folder, run:

```bash
python -m pytest -v
```

## Current Project Status

The API currently runs locally with SQL Server Express. AWS deployment and cloud database integration are future steps; the project is not yet deployed to AWS.

## Future Improvements

- Deploy the API to AWS
- Move the database to a managed cloud database such as Amazon RDS
- Add authentication and role-based access control
- Improve automated test coverage
- Add a frontend dashboard
- Set up continuous integration
