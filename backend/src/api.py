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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

## ROUTES
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks],
    })

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    data = request.get_json()
    print(data)
    if 'title' and 'recipe' not in data:
        abort(422)
    
    drinks = Drink(title=data['title'], recipe=json.dumps(data['recipe']))

    try:
        drinks.insert()
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drinks.long()],
    })

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(jwt,drink_id):
    drinks = Drink.query.get(drink_id)

    try:
        if drinks is None:
            abort(404)
        data =  request.get_json()

        if 'title' in data:
            drinks.title = data['title']
        if 'recipe' in data:
            drinks.recipe = json.dumps(data['recipe'])
        drinks.update()
        return jsonify({
            'success': True,
            'drinks': [drinks.long()],
        })
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt,drink_id):
    try:
        drinks = Drink.query.get(drink_id)

        if drinks is None:
            abort(404)

        drinks.delete()

        return jsonify({
            'success': True,
            'deleted': drinks.id,
        })
    except:
        abort(422)

## Error Handling

@app.errorhandler(401)
def not_found(error):
  return jsonify({
    'success': False,
    'error': 401,
    'message':'unauthorized'
  }), 401

@app.errorhandler(403)
def forbidden(error):
  return jsonify({
    'success': False,
    'error': 403,
    'message':'forbidden'
  }), 403

@app.errorhandler(404)
def unauthorized(error):
  return jsonify({
    'success': False,
    'error': 404,
    'message':'resource not found'
  }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422