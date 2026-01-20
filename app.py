import sys
print("--- Python is reading the file ---")  # This proves the file is running

try:
    from flask import Flask
    from flasgger import Swagger
    
    # Import the Blueprints (Make sure these folder/file names match exactly!)
    from routes.categories import category_bp
    from routes.inventory import inventory_bp
    
    app = Flask(__name__)

    # Configure Swagger
    app.config['SWAGGER'] = {
        'title': 'Inventory Management API',
        'uiversion': 3
    }
    swagger = Swagger(app)

    # Register Blueprints
    app.register_blueprint(category_bp, url_prefix='/categories')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

except Exception as e:
    print(f"\nCRITICAL IMPORT ERROR: {e}")
    print("Check that your folder structure matches:")
    print("  - routes/categories.py")
    print("  - routes/inventory.py")
    sys.exit(1)

if __name__ == '__main__':
    print("------------------------------------------------")
    print("✅ Server starting...")
    print("👉 Local URL: http://127.0.0.1:8089/apidocs") 
    print("------------------------------------------------")
    
    app.run(
        host='0.0.0.0',       
        port=8089,           
        debug=False,         
        use_reloader=False   
    )
