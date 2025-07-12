from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from routes.datasets import datasets_bp
from routes.quality_logs import quality_logs_bp
from utils.database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_db()
    
    CORS(app)
    
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Dataset Catalog API",
            "description": "A lightweight API for managing datasets and quality logs",
            "version": "1.0.0"
        },
        "host": "localhost:5000",
        "basePath": "/",
        "schemes": ["http"]
    })
    

    init_db()
    
    app.register_blueprint(datasets_bp)
    app.register_blueprint(quality_logs_bp)
    
    @app.route('/')
    def index():
        return {
            "message": "Dataset Catalog API",
            "version": "1.0.0",
            "docs": "/apidocs"
        }
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
