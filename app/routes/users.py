from flask import Blueprint, current_app, jsonify, request, session, render_template, flash, redirect, url_for, abort
from bson.objectid import ObjectId
import pymongo
import pymongo.errors
from .flashcards import flashcard_bp
from ..models.user import get_user_by_id, delete_user_by_id, get_users, create_user, save_user, login_and_validate_user
from ..models.schema import UserSchema
from ..utils.security import validate_form
from marshmallow import ValidationError
from werkzeug.security import check_password_hash


user_bp = Blueprint('users', __name__, url_prefix='/users')
user_bp.register_blueprint(flashcard_bp)#, url_prefix='/<user_id>')

# You can test this out by doing curl http://127.0.0.1:5000/users, might not be the path we used in the end but it works for now
# GET /users
# Returns all users in the database

#
# COMMENTING OUT BECAUSE WE DON'T HAVE ADMIN FUNCTIONALITY
#
# @user_bp.route('/', methods=['GET'])
# def get_users_route():  
#     # db = current_app.config['DB']
#     # users_collection = db['users']

#     try:
#         #users = list(users_collection.find({}, {'_id': 0}))
#         users = get_users()
#         if not users:
#             return ({"error": "Error: Collection found to have no users"}, 404)
        
#     except pymongo.error.PyMongoError:
#         return jsonify({"error": "Error: Unable to retrieve all users from database"}, 404)
    
#     return jsonify(users), 200

# POST /users
# Creates a new user
# Returns a success message if a new user was created
# Need something that checks if email is already used to create account.
@user_bp.route("/", methods=['POST'])
def create_user_route():
    form_data, err = validate_form(request.form)
    if err:
        abort(403)

    # Construct user object with submitted form
    user = form_data
    try:
        validated_user = create_user(user)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 404
    
    try:
        saved_user_id = save_user(validated_user)
        if not saved_user_id:
            return jsonify({"error": "Error: Saving was unsuccessful"}), 400
    except:
        return jsonify({"error": "Error: Unable to save user"}), 404

    flash("Successfully created an account")
    return redirect(url_for('main.show'))

# GET /users/<user_id>
# Returns a user based on their user_id in the form of a dictionary
@user_bp.route('/<user_id>')
def get_user_by_id_route(user_id):
    #db = current_app.config['DB']
    #users_collection = db['users']

    try:
        #user = users_collection.find_one({"_id": ObjectId(user_id) })
        user = get_user_by_id(user_id)

        if not user:
            return jsonify({"error": "User is none"}), 404
    except pymongo.errors.PyMongoError:
        return jsonify({"error": "No user exists with that ID or Database error"}), 404

    #user['_id'] = str(user['_id'])
    # if not user:
    #     return jsonify({"error": "User was not properly populated and is null"}, 404)
    
    return jsonify(user), 200


# DELETE /users/<user_id>
# This would need to be modified to include some sort of credential tracking first, can't have any old user deleting people after all...
@user_bp.route('/<user_id>', methods=["DELETE"])
def del_user_by_id_route(user_id):
    # db = current_app.config['DB']
    # users_collection = db['users']
    
    try:
        is_deleted = delete_user_by_id(user_id)
        # deleted = users_collection.delete_one({"_id": ObjectId(user_id)})
        if not is_deleted:
            return jsonify({"error": "Error: User not found"}), 404
        
    except pymongo.errors.PyMongoError:
        return jsonify({"error": "Database connection error"}), 400

    return {"Message": "Successful deletion"}, 200



# PUT /users/<user_id>
# Could be used for updating passwords, not sure yet..
# @user_bp.route('/<user_id>', methods=["PUT"])
# def update_user_by_id(user_id, updated_value):


# POST /users/login
# When a user clicks login in the login page, the request should include the email and password, that password is checked through a hash
# and a session is created with the user id and the email
@user_bp.route('/login', methods=["POST", "GET"])
def login_user():  
    if session.get('user_id'):
        return redirect(url_for('flashcards.get_all_users_sets_home'))
    
    if request.method == "GET":
        return render_template('loginsignup.html')

    logged_in = login_and_validate_user(request)
    if logged_in:
        return redirect(url_for('flashcards.get_all_users_sets_home'))
    else:
        return jsonify({"error": "You were unable to login, please check email or password"}), 401
    

# POST /users/logout
# Very simply just clears the session if there's a user actively logged in
@user_bp.route("/logout", methods=["GET"])
def logout_user():
    try:
        if 'user_id' not in session:
            return jsonify({"error": "There is no user logged in"}), 401

        session.clear()
        return render_template('index.html')
    except Exception as e:
        print(f"Logout Error: {e}")
        return jsonify({"error": "An error occurred during logout"}), 500

@user_bp.route('/profile', methods=['GET'])
def get_profile_page():
    if session.get('user_id'):
        return render_template('profile.html')
    else:
        return redirect(url_for('users.login_user'))
