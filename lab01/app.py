from flask import Flask, request, Response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from flask_cors import CORS
from hashlib import sha256
from db_manager import *

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'veeeeeery_secret_key'
jwt = JWTManager(app)
# CORS(app)

def get_password_hash(password: str):
    code = sha256(password.encode()).hexdigest()
    return code

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if get_user_by_login(data['login']):
        return jsonify({'message': 'User already exists'}), 400
    user = create_user(data['login'], get_password_hash(data['password']))
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'success'}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = get_user_by_login(data['login'])
    if user and user.password == get_password_hash(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'message': 'Success', 'jwt': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401
    
@app.route("/api/books", methods=["GET"])
@jwt_required()
def all_booksGET():
    books = get_all_books()
    if books:
        return jsonify([{"id": book.id, "name": book.name, "description": book.description, "size": book.size} for book in books]), 200

@app.route("/api/books/<int:id>", methods=["GET"])
@jwt_required()
def booksGET(id: int):
    book = get_book(id)
    if book:
        return jsonify({"id": book.id, "name": book.name, "description": book.description, "size": book.size}), 200
    

@app.route("/api/books/", methods=["POST"])
@jwt_required()
def booksPOST():
    data = request.get_json()
    book = create_book(data["name"], data["size"], data["description"])
    if book:
        return jsonify({"id": book.id, "name": book.name, "description": book.description, "size": book.size}), 201
    
@app.route("/api/books/<id>", methods=["PUT"])
@jwt_required()
def booksPUT(id: int):
    data = request.get_json()
    book = edit_book(id, data["name"], data["size"], data["description"])
    if book:
        return jsonify({"id": book.id, "name": book.name, "description": book.description, "size": book.size}), 200
    
@app.route("/api/books/<id>", methods=["DELETE"])
@jwt_required()
def booksDELETE(id: int):
    book = delete_book(id)
    return jsonify({"message": "Deleted successfully"}), 200


@app.route("/", methods=["GET"])
def main():
    if request.method == "GET":
        return "server is running"

if __name__ == "__main__":
    app.run(debug=True)