from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import uuid

reviews_bp = Blueprint('reviews', __name__)

#Helper function to recalc the restaurant ratingA
def recalc_restaurant_rating(db, restaurant_id):
    reviews = list(db.reviews.find({"restaurant_id": restaurant_id}))
    if not reviews:
        db.restaurants.update_one({"_id": restaurant_id}, {"$set": {"hygiene_rating": None}})
        return

    avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
    db.restaurants.update_one(
        {"_id": restaurant_id},
        {"$set": {"hygiene_rating": avg_rating}}
    )


#Add a review
@reviews_bp.route('/<restaurant_id>', methods=['POST'])
@jwt_required()
def add_review(restaurant_id):
    db = current_app.db
    uid = get_jwt_identity()
    user = db.users.find_one({"_id": uid})

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(force=True)

    #Validate rating
    rating = data.get("rating")
    if rating is None or not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be 1-5"}), 400

    review = {
        "_id": str(uuid.uuid4()),
        "restaurant_id": restaurant_id,
        "user_id": uid,
        "rating": int(rating),
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    db.reviews.insert_one(review)
    recalc_restaurant_rating(db, restaurant_id)

    return jsonify(review), 201


#Get all reviews for a restaurant
@reviews_bp.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_reviews_for_restaurant(restaurant_id):
    db = current_app.db
    reviews = list(db.reviews.find({"restaurant_id": restaurant_id}, {"_id": 1, "rating": 1, "title": 1, "body": 1, "user_id": 1, "updated_at": 1}))
    return jsonify(reviews), 200


#Get a specific review
@reviews_bp.route('/<rid>', methods=['GET'])
def get_review(rid):
    db = current_app.db
    review = db.reviews.find_one({"_id": rid}, {"_id": 1, "rating": 1, "title": 1, "body": 1, "user_id": 1, "restaurant_id": 1})
    if not review:
        return jsonify({"error": "Review not found"}), 404
    return jsonify(review), 200


#Update a review
@reviews_bp.route("/<review_id>", methods=["PUT"])
@jwt_required()
def update_review(review_id):
    db = current_app.db  
    uid = get_jwt_identity()
    role = get_jwt().get("role")

    review = db.reviews.find_one({"_id": review_id})
    if not review:
        return jsonify({"error": "Review not found"}), 404

    if role != "admin" and review.get("user_id") != uid:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json(force=True)
    updated = {
        "rating": data.get("rating", review.get("rating")),
        "title": data.get("title", review.get("title")),
        "body": data.get("body", review.get("body")),
        "updated_at": datetime.utcnow().isoformat()
    }

    result = db.reviews.update_one({"_id": review_id}, {"$set": updated})

    return jsonify({"message": "Review updated successfully"}), 200

#Delete a review
@reviews_bp.route('/<rid>', methods=['DELETE'])
@jwt_required()
def delete_review(rid):
    db = current_app.db
    uid = get_jwt_identity()

    review = db.reviews.find_one({"_id": rid})
    if not review:
        return jsonify({"error": "Review not found"}), 404

    if review["user_id"] != uid:
        return jsonify({"error": "Unauthorized"}), 403

    db.reviews.delete_one({"_id": rid})
    recalc_restaurant_rating(db, review["restaurant_id"])

    return jsonify({"msg": "Review deleted"}), 200
