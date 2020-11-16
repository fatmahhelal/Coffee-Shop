import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES

# endpoint to GET requests for all available drinks short


@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        # abort 404 if no drinks available
        if len(drinks) == 0:
            abort(404)

        # return success response
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })
    except Exception:
        abort(500)


# endpoint to GET requests for all available drinks long
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):

    try:
        drinks = Drink.query.all()
        # abort 404 if no drinks available
        if len(drinks) == 0:
            abort(404)

    # return success response
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except Exception:
        abort(500)


# endpoint to POST a new drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    # get the enterd data from client
    body = request.get_json()

    # abort 422 if the requst is bad
    if not ('title' in body and 'recipe' in body):
        abort(400)

    # get the new drink's informatin
    new_title = body['title']
    new_recipe = body['recipe']

    # create a new drink
    try:
        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()

    # return success response
        return jsonify({
            "success": True,
            "drinks": drink.long()
        })
    except Exception:
        abort(422)


# endpoint to PATCH drink using a its ID.
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, id):

    # get the enterd data from client
    bady = request.get_json()
    new_title = bady.get('title', None)

    # get drink information by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # returns a 404 error if drink is not found
    if drink is None:
        abort(404)

    # returns a 400 error if  title None
    if new_title is None:
        abort(400)

    try:
        # update drink in the database
        drink.title = new_title
        drink.update()

    # return success response
        return jsonify({
            'success': True,
            'drinks': drink.long(),
        })
    except Exception:
        abort(422)


# endpoint to DELETE drink using a its ID.
@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):

    # get the drink by its id to DELETE
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # abort 404 if the drink not found
    if drink is None:
        abort(404)

    # delete the drink
    drink.delete()

    # return success response
    return jsonify({
         'success': True,
         'delete': id
     })


# Error Handling for all expected errors 400, 403, and AuthError.
@app.errorhandler(404)
def not_found(error):
    return jsonify({
       "success": False,
       "error": 404,
       "message": "resource not found"
        }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
            "success": False,
            "error": 403,
            "message": "forbidden"
        }), 403


@app.errorhandler(405)
def unallowed_method(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
        }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
        }), 500

# error handler for AuthError


@app.errorhandler(AuthError)
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
