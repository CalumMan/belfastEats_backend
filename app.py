from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_cors import CORS
import os

# load .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change_me")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/belfast_eats")

    #Prevent auth token expiry (during development phase)
    from datetime import timedelta
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)

    # Connect MongoDB
    client = MongoClient(app.config["MONGO_URI"])
    default_db = client.get_default_database()
    db = default_db if default_db is not None else client["belfast_eats"]
    app.db = db


    # Init JWT
    JWTManager(app)

    # Register blueprints (import here to avoid circular imports)
    from routes.auth import auth_bp
    from routes.restaurants import restaurants_bp
    from routes.reviews import reviews_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1.0/auth")
    app.register_blueprint(restaurants_bp, url_prefix="/api/v1.0/restaurants")
    app.register_blueprint(reviews_bp, url_prefix="/api/v1.0/reviews")

    @app.route('/')
    def home():
        return jsonify({"msg":"Belfast Eats API is running"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)