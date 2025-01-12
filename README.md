# inventory_management_api
This is a MVP Inventory Management API.

Django Project: inventory_api
Django App: inventory


# Inventory Management API - Authentication Setup

This API uses Token-based authentication. Below is the setup and instructions for testing the authentication.

API Documentation

User Registration
Endpoint: /register
Method: POST
Required Fields:
username
password
confirm_password
first_name
last_name
User Login
Endpoint: /login
Method: POST
Required Fields:
username
password
User Profile
Endpoint: /profile
Methods:
GET: Retrieves user profile data based on a generated JWT token.
PUT: Updates user details.

API Items Creation
Endpoint: /items
Method: POST
Required Fields:
id (auto-generated)
name
description
price
quantity
category
managed_by (derived from user profile)
Items List
Endpoint: /items
Method: GET
Functionality: Retrieves information about all items in the inventory.

Inventory Update Quantity
Endpoint: /inventory/update-quantity
Method: POST
Required Fields:
item_id
quantity (new quantity to update)
Inventory Detail
Endpoint: /inventory/{item_id}
Methods:
GET: Retrieves details of a specific inventory item.
PUT: Updates the details of an inventory item.
DELETE: Deletes an item from the inventory (authorized users only).

Change Log
Endpoint: /change-log
Method: GET
Functionality: Displays changes made to items, including:
item_id
old_quantity
new_quantity
user (who made the change)
timestamp

Inventory History
Endpoint: /inventory/history/{item_id}
Method: GET
Functionality: Displays the entire history of changes for a specific item based on its ID.

