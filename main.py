from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import jwt
from functools import wraps
from bson import ObjectId
import secrets

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017'
app.config['SECRET_KEY'] = secrets.token_hex(32)
mongo = PyMongo(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token.split(" ")[1], )
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(data, *args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()    
    mongo.db.users.insert_one(data)
    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    user = mongo.db.users.find_one({'email': auth['email']})

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if auth['password'] == user['password']:
        token = jwt.encode({'email': auth['email']}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

# Template CRUD operations
@app.route('/template', methods=['POST'])
@token_required
def create_template(current_user):
    data = request.get_json()
    # Insert template data into MongoDB
    mongo.db.templates.insert_one(data)
    return jsonify({'message': 'Template created successfully!'}), 201

@app.route('/template', methods=['GET'])
@token_required
def get_all_templates(current_user):
    templates = list(mongo.db.templates.find())
    return jsonify({'templates': templates}), 200

@app.route('/template/<template_id>', methods=['GET'])
@token_required
def get_template(current_user, template_id):
    template = mongo.db.templates.find_one({'_id': ObjectId(template_id)})
    if template:
        return jsonify({'template': template}), 200
    return jsonify({'message': 'Template not found'}), 404

@app.route('/template/<template_id>', methods=['PUT'])
@token_required
def update_template(current_user, template_id):
    data = request.get_json()
    # Update template data in MongoDB
    result = mongo.db.templates.update_one({'_id': ObjectId(template_id)}, {'$set': data})
    if result.modified_count > 0:
        return jsonify({'message': 'Template updated successfully'}), 200
    return jsonify({'message': 'Template not found'}), 404

@app.route('/template/<template_id>', methods=['DELETE'])
@token_required
def delete_template(current_user, template_id):
    # Delete template data from MongoDB
    result = mongo.db.templates.delete_one({'_id': ObjectId(template_id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'Template deleted successfully'}), 200
    return jsonify({'message': 'Template not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
