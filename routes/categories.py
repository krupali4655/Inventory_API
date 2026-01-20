# 19/01/2026
from flask import Blueprint, jsonify, request
from db import get_db_connection

category_bp = Blueprint('categories', __name__)

# ===========================
# 1. CREATE CATEGORY (POST)

@category_bp.route('/', methods=['POST'])
def add_category():
    """
    Create a new category
    ---
    tags:
      - Categories
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: {type: string, example: "Electronics"}
            description: {type: string, example: "Gadgets and devices"}
    responses:
      201:
        description: Category created successfully
      400:
        description: Error creating category
    """
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id;",
                (name, description)
            )
            cat_id = cursor.fetchone()[0]
            conn.commit()
            return jsonify({"message": "Category created", "id": cat_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===========================
# 2. GET ALL CATEGORIES (GET)

@category_bp.route('/', methods=['GET'])
def get_categories():
    """
    Get all categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description FROM categories ORDER BY id;")
            rows = cursor.fetchall()
            
            categories = []
            for row in rows:
                categories.append({"id": row[0], "name": row[1], "description": row[2]})
            
            return jsonify(categories), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===========================
# 3. GET CATEGORY STOCK (Stored Function)
# URL becomes: /categories/1/stock

@category_bp.route('/<int:category_id>/stock', methods=['GET'])
def get_category_stock(category_id):
    """
    Get total stock count for a category (Uses DB Function)
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Returns total stock count
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Calling the PostgreSQL function
            cursor.callproc('get_total_stock', [category_id])
            
            # The result is returned as a single row
            total_stock = cursor.fetchone()[0]
            
            if total_stock is None:
                total_stock = 0

            return jsonify({
                "category_id": category_id,
                "total_stock": total_stock
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===========================
# 4. APPLY DISCOUNT (Stored Function)
# URL becomes: /categories/1/discount


@category_bp.route('/<int:category_id>/discount', methods=['POST'])
def apply_discount(category_id):
    """
    Apply a percentage discount to all items in a category
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            percentage: {type: number, example: 10}
    responses:
      200:
        description: Discount applied
    """
    data = request.get_json()
    percentage = data.get('percentage')

    if percentage is None or percentage <= 0 or percentage >= 100:
        return jsonify({"error": "Percentage must be between 0 and 100"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Call the stored function
            cursor.callproc('apply_category_discount', [category_id, percentage])
            
            updated_count = cursor.fetchone()[0]
            conn.commit()
            
            return jsonify({
                "message": f"Discount of {percentage}% applied successfully",
                "items_updated": updated_count
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===========================
# 5. REMOVE DISCOUNT (Stored Function)
# URL becomes: /categories/1/remove-discount

@category_bp.route('/<int:category_id>/remove-discount', methods=['POST'])
def remove_discount(category_id):
    """
    Revert a discount (Restore original prices)
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            percentage: {type: number, example: 10}
    responses:
      200:
        description: Prices restored
    """
    data = request.get_json()
    percentage = data.get('percentage')

    if percentage is None or percentage <= 0 or percentage >= 100:
        return jsonify({"error": "Percentage must be > 0 and < 100"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc('remove_category_discount', [category_id, percentage])
            updated_count = cursor.fetchone()[0]
            conn.commit()
            
            return jsonify({
                "message": f"Discount of {percentage}% removed. Prices restored.",
                "items_updated": updated_count
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500