# Bank System API

A secure and production-ready RESTful banking API built with Django REST Framework and PostgreSQL.

## Features

* JWT Authentication (Register, Login, Refresh, Logout with Blacklisting)
* Bank Account Management (Create & List Accounts)
* Secure Deposit & Withdrawal Transactions
* Atomic Balance Updates for Data Consistency
* Transaction Filtering (date, type, amount, account)
* CSV Export & Financial Reports
* Admin Dashboard with Analytics
* Standardized API Response Format
* OpenAPI Documentation (Swagger UI)

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* SimpleJWT
* drf-spectacular (OpenAPI / Swagger)
* django-cors-headers
* python-decouple

## Installation

```bash
git clone <repo-url>
cd bank-system

python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

## API Documentation

* Swagger UI: `/api/docs/`
* OpenAPI Schema: `/api/schema/`

## Authentication

All protected endpoints require JWT token:

```
Authorization: Bearer <access_token>
```

## Example Endpoints

### Register User

POST `/api/register/`

### Login

POST `/api/token/`

### Create Bank Account

POST `/api/bank-accounts/`

### Deposit / Withdraw

POST `/api/transactions/`

### Reports

GET `/api/reports/transactions/`

## Project Structure

* users/ → authentication system
* bankaccount/ → accounts & transactions
* reports/ → analytics & exports
* core/ → shared utilities & helpers
* config/ → project settings

## Key Highlights

* Service-layer architecture for clean separation of logic
* Atomic transactions for safe balance updates
* Role-based access control
* Optimized filtering and reporting system
* Secure and scalable API design

## License

This project is for educational and portfolio purposes.
