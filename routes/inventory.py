# 19/01/2026
from flask import Blueprint, jsonify, request
from db import get_db_connection
from psycopg2.errors import ForeignKeyViolation


inventory_bp = Blueprint('inventory', __name__)


# 1. CREATE ITEM (POST)

@inventory_bp.route('/', methods=['POST'])
def add_item():
    """
    Add a new item to inventory
    ---
    tags:
      - Inventory
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            product_name: {type: string, example: "Laptop"}
            category_id: {type: integer, example: 1}
            quantity: {type: integer, example: 50}
            price: {type: number, example: 999.99}
    responses:
      201:
        description: Item added successfully
      400:
        description: Invalid input or Category ID not found
    """
    data = request.get_json()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO inventory (product_name, category_id, quantity, price) 
                   VALUES (%s, %s, %s, %s) RETURNING id;""",
                (data['product_name'], data['category_id'], data['quantity'], data['price'])
            )
            item_id = cursor.fetchone()[0]
            conn.commit()
            return jsonify({"message": "Item added", "id": item_id}), 201
            
    except ForeignKeyViolation: 
        return jsonify({"error": "Category ID not found. Please create the category first."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# 2. GET ALL ITEMS (GET)

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """
    Get all inventory items
    ---
    tags:
      - Inventory
    responses:
      200:
        description: List of items
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory ORDER BY id;")
            rows = cursor.fetchall()
            
            inventory = []
            for row in rows:
                inventory.append({
                    "id": row[0], 
                    "product_name": row[1], 
                    "category_id": row[2], 
                    "quantity": row[3], 
                    "price": float(row[4])
                })
            return jsonify(inventory), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# 3. GET SINGLE ITEM (GET)

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    """
    Get a single inventory item by ID
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Item found
      404:
        description: Item not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE id = %s;", (item_id,))
            row = cursor.fetchone() 
            
            if row is None:
                return jsonify({"error": "Item not found"}), 404

            item = {
                "id": row[0],
                "product_name": row[1],
                "category_id": row[2],
                "quantity": row[3],
                "price": float(row[4])
            }
            return jsonify(item), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# 4. UPDATE ITEM (PUT)

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update an inventory item quantity or price
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            quantity: {type: integer}
            price: {type: number}
    responses:
      200:
        description: Item updated
      404:
        description: Item not found
    """
    data = request.get_json()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET quantity = %s, price = %s WHERE id = %s;",
                (data['quantity'], data['price'], item_id)
            )
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Item not found"}), 404
                
            return jsonify({"message": "Item updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# 5. DELETE ITEM (DELETE)

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Delete an item
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Item deleted
      404:
        description: Item not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = %s;", (item_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Item not found"}), 404
                
            return jsonify({"message": "Item deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# 6. LOW STOCK CHECK (GET)

@inventory_bp.route('/low-stock/<int:threshold>', methods=['GET'])
def get_low_stock_items(threshold):
    """
    Get items with stock below a certain level (Uses DB Function)
    ---
    tags:
      - Inventory
    parameters:
      - name: threshold
        in: path
        type: integer
        required: true
        description: The quantity limit (e.g., 10)
    responses:
      200:
        description: List of low stock items
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # We execute the function like a table
            cursor.execute("SELECT * FROM get_low_stock(%s);", (threshold,))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "product_name": row[1],
                    "quantity": row[2]
                })

            return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500