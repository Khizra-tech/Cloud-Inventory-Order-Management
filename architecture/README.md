# Cloud Architecture

## Project
Cloud-Based Inventory and Order Management System

## Main Components
User interface: Allow the business owner to manage inventory.
API Gateway: Recieves requests from the application.
AWS Lambda: Processes business logics and inventory operatons.
Amazon DynamoDB: Stores product and order records.
Amazon CloudWatch: Monitord applications activity and errors.
AWS IAM: Control permissions for accessing cloud resources.

## Data Flow
the user interacts with the application.
The application sends requests to the API.
Lambda processes requests and accesses the database.
the API returns the results to the application.

## Security 
Use least-privilege permissions and keep credentials out of the repository.
