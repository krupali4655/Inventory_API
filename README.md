# 📦 Inventory Management API

A modular RESTful API built with **Flask**, **PostgreSQL**, and **Pydantic**.
This API manages product inventory and categories, featuring **robust data validation**, **database connection pooling**, and **interactive documentation**.

### 🚀 Key Features
* **Modular Architecture**: Organized using Flask Blueprints (`routes/`).
* **Strong Validation**: Uses **Pydantic** schemas to block invalid data (e.g., negative prices) before it touches the database.
* **High Performance**: Implements `psycopg2` connection pooling.
* **Interactive Docs**: Integrated **Swagger UI** for testing endpoints.

---

## 📂 Project Structure

```text
/inventory-api
├── app.py                # Application Entry Point & Config
├── db.py                 # Database Connection Pool & Executors
├── schemas.py            # Pydantic Validation Models (Rules)
├── schema.sql            # Database Table Definitions
├── requirements.txt      # Python Dependencies
└── routes/               # API Route Modules (Blueprints)
    ├── categories.py     # Category Logic (Create, List, Stock)
    └── inventory.py      # Inventory Logic (CRUD operations)

```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

* Python 3.8+
* PostgreSQL installed and running.

### 2. Database Setup

1. Create a database (e.g., `inventory_db`).
2. Run the script inside `schema.sql` to create the tables and functions.
3. Create a `.env` file in the root folder:
```
DB_HOST=localhost
DB_NAME=db name
DB_USER= username
DB_PASS=your_password
DB_PORT=5432

```



### 3. Install & Run

```
# Install dependencies
pip install flask psycopg2-binary python-dotenv flasgger flask-cors pydantic

# Run the server
python app.py

```

> The server will start on **Port 8089**.

---

The API comes with built-in **Swagger UI**.
Once running, visit:

👉 **http://localhost:8089/apidocs**

```

```
