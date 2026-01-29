from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import uuid, os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    db = current_app.db
    data = request.get_json(force=True)
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error':'Missing required fields'}), 400

    if db.users.find_one({'email': data['email']}):
        return jsonify({'error':'Email already exists'}), 400

    # role handling
    desired_role = data.get('role', 'user')
    if desired_role == 'admin':
        invite_code = data.get('invite_code')
        if invite_code is None or invite_code != os.getenv('ADMIN_INVITE_CODE'):
            return jsonify({'error':'Invalid admin invite code'}), 403

    user = {
        '_id': str(uuid.uuid4()),
        'username': data.get('username', data['email'].split('@')[0]),
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'role': desired_role if desired_role in ['user','admin'] else 'user',
        'created_at': datetime.utcnow().isoformat()
    }
    db.users.insert_one(user)
    user_no_pw = {k:v for k,v in user.items() if k != 'password_hash'}
    return jsonify(user_no_pw), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    db = current_app.db
    data = request.get_json(force=True)
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error':'Missing credentials'}), 400

    user = db.users.find_one({'email': data['email']})
    if not user or not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'error':'Invalid credentials'}), 401

    # Include role in JWT custom claims
    claims = {'role': user.get('role', 'user')}
    access_token = create_access_token(identity=user['_id'], additional_claims=claims)
    return jsonify({'access_token': access_token, 'user_id': user['_id'], 'role': claims['role']}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    db = current_app.db
    uid = get_jwt_identity()
    user = db.users.find_one({'_id': uid}, {'password_hash': 0})
    if not user:
        return jsonify({'error':'User not found'}), 404
    return jsonify(user), 200
