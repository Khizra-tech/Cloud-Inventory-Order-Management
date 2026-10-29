import pyodbc

connection_string = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    r"DATABASE=CloudInventoryDB;"
    r"Trusted_Connection=yes;"
)

try:
    connection = pyodbc.connect(connection_string)
    print("Connected to SQL Server successfully!")

    cursor = connection.cursor()
    cursor.execute(
        "SELECT ProductID, NAME, price, quantity FROM dbo.Products"
    )

    products = cursor.fetchall()

    print("\nProduct List:")
    for product in products:
        print(product)

    connection.close()

except pyodbc.Error as error:
    print("Database connection failed:")
    print(error)