from flask import Blueprint, jsonify, request
from debug_db import execute_read, execute_change
from schemas import CategoryCreateSchema
from pydantic import ValidationError

category_bp = Blueprint('categories', __name__)

# ===========================
# 1. GET ALL CATEGORIES
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
    rows, error = execute_read("SELECT id, name, description FROM categories ORDER BY id;")
    if error: return jsonify({"error": error}), 500
    
    categories = [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]
    return jsonify(categories), 200

# ===========================
# 2. CREATE CATEGORY (Updated with Pydantic)
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
            name:
              type: string
              example: "Electronics"
            description:
              type: string
              example: "Gadgets"
    responses:
      201:
        description: Category created
      400:
        description: Validation Error
    """
    try:
        # 1. VALIDATE DATA
        body = CategoryCreateSchema(**request.get_json())
        
        # 2. EXECUTE DB CHANGE
        # Note: We use body.name and body.description now
        row, error = execute_change(
            "INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id;",
            (body.name, body.description),
            returning=True
        )
        
        if error: return jsonify({"error": error}), 400
        return jsonify({"message": "Category created", "id": row[0]}), 201

    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400

# ===========================
# 3. GET STOCK
@category_bp.route('/<int:category_id>/stock', methods=['GET'])
def get_category_stock(category_id):
    """
    Get stock count for a category
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
        description: Total stock count
    """
    row, error = execute_read("SELECT get_total_stock(%s);", (category_id,))
    if error: return jsonify({"error": error}), 500
    total = row[0][0] if row and row[0][0] is not None else 0
    return jsonify({"category_id": category_id, "total_stock": total}), 200

