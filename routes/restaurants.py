from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_cors import cross_origin
from routes._authz import admin_required
import uuid

restaurants_bp = Blueprint('restaurants', __name__)


# -------------------------------------------------------------------
# GET ALL RESTAURANTS  (client-side pagination in Angular)
# -------------------------------------------------------------------
@restaurants_bp.route("/", methods=["GET"])
@cross_origin()
def get_restaurants():
    db = current_app.db

    # Return ALL restaurants; Angular will paginate/filter/sort
    restaurants = list(db.restaurants.find())

    # Make sure _id is a string for JSON / Angular
    for r in restaurants:
        r["_id"] = str(r.get("_id", ""))

    return jsonify(restaurants), 200


# -------------------------------------------------------------------
# GET SINGLE RESTAURANT
# -------------------------------------------------------------------
@restaurants_bp.route("/<string:rid>", methods=["GET"])
@cross_origin()
def get_restaurant(rid):
    db = current_app.db
    r = db.restaurants.find_one({"_id": rid})

    if not r:
        return jsonify({"error": "Not found"}), 404

    r["_id"] = str(r.get("_id", ""))
    return jsonify(r), 200


# -------------------------------------------------------------------
# CREATE RESTAURANT
# -------------------------------------------------------------------
@restaurants_bp.route("/", methods=["POST"])
@cross_origin()
@jwt_required()
def create_restaurant():
    db = current_app.db
    data = request.get_json(force=True)

    required = ["name", "address", "postcode", "hygiene_rating", "cuisine", "tags"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    new = {
        "_id": str(uuid.uuid4()),
        "name": data["name"],
        "address": data["address"],
        "postcode": data["postcode"],
        "hygiene_rating": int(data["hygiene_rating"]),
        "cuisine": data["cuisine"],
        "tags": data["tags"],
        "created_by": get_jwt_identity(),
    }

    db.restaurants.insert_one(new)
    new["_id"] = str(new["_id"])
    return jsonify(new), 201


# -------------------------------------------------------------------
# UPDATE RESTAURANT
# -------------------------------------------------------------------
@restaurants_bp.route("/<string:rid>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_restaurant(rid):
    db = current_app.db
    data = request.get_json(force=True)

    existing = db.restaurants.find_one({"_id": rid})
    if not existing:
        return jsonify({"error": "Not found"}), 404

    uid = get_jwt_identity()
    role = get_jwt().get("role", "user")
    if existing.get("created_by") != uid and role != "admin":
        return jsonify({"error": "Not permitted"}), 403

    updatable = {}
    for k in ["name", "address", "postcode", "hygiene_rating", "cuisine", "tags"]:
        if k in data:
            updatable[k] = int(data[k]) if k == "hygiene_rating" else data[k]

    if not updatable:
        return jsonify({"error": "No updatable fields provided"}), 400

    db.restaurants.update_one({"_id": rid}, {"$set": updatable})
    updated = db.restaurants.find_one({"_id": rid})
    updated["_id"] = str(updated["_id"])
    return jsonify(updated), 200


# -------------------------------------------------------------------
# DELETE RESTAURANT
# -------------------------------------------------------------------
@restaurants_bp.route("/<string:rid>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_restaurant(rid):
    db = current_app.db
    existing = db.restaurants.find_one({"_id": rid})
    if not existing:
        return jsonify({"error": "Not found"}), 404

    uid = get_jwt_identity()
    role = get_jwt().get("role", "user")
    if existing.get("created_by") != uid and role != "admin":
        return jsonify({"error": "Not permitted"}), 403

    db.restaurants.delete_one({"_id": rid})
    return jsonify({"msg": "Deleted"}), 204


# -------------------------------------------------------------------
# SEARCH BY CUISINE
# -------------------------------------------------------------------
@restaurants_bp.route("/search/cuisine", methods=["GET"])
@cross_origin()
def search_by_cuisine():
    db = current_app.db
    cuisine = request.args.get("cuisine")

    if not cuisine:
        return jsonify({"error": "Cuisine query parameter is required"}), 400

    result = list(
        db.restaurants.find(
            {"cuisine": {"$regex": cuisine, "$options": "i"}},
            {"_id": 1, "name": 1, "cuisine": 1, "hygiene_rating": 1},
        )
    )

    for r in result:
        r["_id"] = str(r.get("_id", ""))

    return jsonify(result), 200


# -------------------------------------------------------------------
# FILTER BY MIN RATING
# -------------------------------------------------------------------
@restaurants_bp.route("/rating/<int:min_rating>", methods=["GET"])
@cross_origin()
def get_restaurants_by_rating(min_rating):
    db = current_app.db
    restaurants = list(
        db.restaurants.find({"hygiene_rating": {"$gte": min_rating}})
    )

    for r in restaurants:
        r["_id"] = str(r.get("_id", ""))

    return jsonify(restaurants), 200


# -------------------------------------------------------------------
# SEARCH BY NAME (optional helper)
# -------------------------------------------------------------------
@restaurants_bp.route("/search", methods=["GET"])
@cross_origin()
def search_restaurants():
    db = current_app.db
    name_query = request.args.get("name", "")

    results = list(
        db.restaurants.find(
            {"BusinessName": {"$regex": name_query, "$options": "i"}}
        )
    )

    for r in results:
        r["_id"] = str(r.get("_id", ""))

    return jsonify(results), 200
