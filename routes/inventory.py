from flask import Blueprint, jsonify, request
from debug_db import execute_read, execute_change
from schemas import ItemCreateSchema, ItemUpdateSchema
from pydantic import ValidationError

inventory_bp = Blueprint('inventory', __name__)

# ===========================
# 1. GET ALL ITEMS
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
    rows, error = execute_read("SELECT * FROM inventory ORDER BY id;")
    if error: return jsonify({"error": error}), 500
    
    inventory = []
    for r in rows:
        inventory.append({
            "id": r[0], "product_name": r[1], "category_id": r[2], 
            "quantity": r[3], "price": float(r[4])
        })
    return jsonify(inventory), 200

# ===========================
# 2. CREATE ITEM (Updated with Pydantic)
@inventory_bp.route('/', methods=['POST'])
def add_item():
    """
    Add a new item
    ---
    tags:
      - Inventory
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [product_name, category_id]
          properties:
            product_name: {type: string, example: "Laptop"}
            category_id: {type: integer, example: 1}
            quantity: {type: integer, example: 10}
            price: {type: number, example: 999.99}
    responses:
      201:
        description: Item created
      400:
        description: Validation Error
    """
    try:
        # 1. VALIDATE DATA
        body = ItemCreateSchema(**request.get_json())

        # 2. EXECUTE DB CHANGE
        # Note: We access fields using dot notation (body.product_name)
        row, error = execute_change(
            """INSERT INTO inventory (product_name, category_id, quantity, price) 
               VALUES (%s, %s, %s, %s) RETURNING id;""",
            (body.product_name, body.category_id, body.quantity, body.price),
            returning=True
        )
        if error: return jsonify({"error": error}), 400
        return jsonify({"message": "Item added", "id": row[0]}), 201

    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400

# ===========================
# 3. GET SINGLE ITEM
@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    """
    Get a single item by ID
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
        description: Item details
      404:
        description: Item not found
    """
    rows, error = execute_read("SELECT * FROM inventory WHERE id = %s;", (item_id,))
    if error: return jsonify({"error": error}), 500
    if not rows: return jsonify({"error": "Item not found"}), 404

    r = rows[0]
    item = {
        "id": r[0], "product_name": r[1], "category_id": r[2], 
        "quantity": r[3], "price": float(r[4])
    }
    return jsonify(item), 200

# ===========================
# 4. UPDATE ITEM (Updated with Pydantic)
@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update an item's quantity or price
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
            quantity: {type: integer, example: 50}
            price: {type: number, example: 899.99}
    responses:
      200:
        description: Item updated
      400:
        description: Validation Error
    """
    try:
        # 1. VALIDATE DATA (allows optional fields)
        body = ItemUpdateSchema(**request.get_json())

        # 2. EXECUTE DB CHANGE
        # We use body.quantity and body.price. They will be None if not provided.
        _, error = execute_change(
            "UPDATE inventory SET quantity = %s, price = %s WHERE id = %s;",
            (body.quantity, body.price, item_id)
        )
        if error: return jsonify({"error": error}), 400
        return jsonify({"message": "Item updated"}), 200

    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400

# ===========================
# 5. DELETE ITEM
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
    """
    _, error = execute_change("DELETE FROM inventory WHERE id = %s;", (item_id,))
    if error: return jsonify({"error": error}), 500
    return jsonify({"message": "Item deleted"}), 200

