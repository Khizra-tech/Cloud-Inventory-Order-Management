create database CloudInventoryDB

use CloudInventoryDB

create table products(ProductID int identity(1,1)
primary key,NAME varchar(100) not null, price decimal(10,2) not null
check(price >=0),
quantity int not null default 0 check (quantity >= 0), 
recorderlevel int not null default 5 check( recorderlevel >= 0)
)

create table orders(OrderID int identity(1,1)
primary key, CustomerName varchar(100) not null,
OrderDate datetime2 not null default sysdatetime(),
status varchar(50) not null default 'Pending'
check(status in ('Pending' , 'Processing', 'Completed' , 'Cancelled'))
)

create table OrderItems(OrderItemId int identity(1,1) primary key,
OrderID int not null, ProductID int not null,
quantity int not null check (quantity>0),
unitprice decimal(10,2) not null check (unitprice>=0),
foreign key(OrderID) references orders(OrderID), 
foreign key (ProductID) references products(ProductID))

insert into products(Name, price,quantity,recorderlevel) values
('Wireless Mouse' , 2500.00, 12 , 5 ),
('Mechanical Keyboard' , 7500.00 , 4,5),
('USB-C Cable' , 800.00 , 30, 10),
('Laptop Stand' , 3500.00 , 2,3 )

insert into orders (CustomerName , status) values
('ALI' , 'Pending'), ('Ayesha' , 'Processing')

insert into OrderItems(OrderID , ProductID, quantity, unitprice) values
(1,1,2,2500), (1,3,3,800), (2,2,1,7500)

select *from orders
select * from Products

select o.OrderID, o.customername,p.Name as ProductName, oi.quantity , oi.unitprice,
oi. quantity *oi.unitprice as linetotal, o.status from Orders o 
inner join OrderItems oi on o.OrderID = oi.OrderID inner join Products p on oi.ProductID = p.ProductID

select Name, quantity, recorderlevel  from products where quantity <= recorderlevel


SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Products';