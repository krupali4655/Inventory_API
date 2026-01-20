# 19/01/2026
from flask import Flask
from flasgger import Swagger
from routes.categories import category_bp
from routes.inventory import inventory_bp

app = Flask(__name__)

app.config['SWAGGER'] = {
    'title': 'Inventory Management API',
    'uiversion': 3
}
swagger = Swagger(app)

# 1. Register Categories
# Any route inside category_bp will effectively start with '/categories'
app.register_blueprint(category_bp, url_prefix='/categories')

# 2. Register Inventory
# Any route inside inventory_bp will effectively start with '/inventory'
app.register_blueprint(inventory_bp, url_prefix='/inventory')

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:5000")
    print("Swagger Docs at http://127.0.0.1:5000/apidocs")
    app.run(debug=True)


