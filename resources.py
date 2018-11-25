from flask_jwt_extended import (create_access_token, create_refresh_token,
jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_restful import Resource, reqparse
from models import User, RevokedToken, Cart, ItemCart
from flask import request
from sqlalchemy.orm import Load, load_only
from sqlalchemy.sql import func
import json

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)

        data = parser.parse_args()

        if User.find_by_username(data['username']):
          return {'message': 'User {} already exists'. format(data['username'])}

        new_user = User(
            username = data['username'],
            password = User.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'User {} was created'.format( data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        current_user = User.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {'message': 'Logged in as {}'.format(current_user.username),
                    'access_token': access_token,
                    'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}, 401


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}, 200
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}, 200
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}, 200


class AllUsers(Resource):
    def get(self):
        return User.return_all()

    def delete(self):
        return User.delete_all()

class Baskets(Resource):
    @jwt_required
    def get(self):
        current_user = User.find_by_username(get_jwt_identity())
        return Cart.return_all(current_user.id)

    @jwt_required
    def delete(self, cart_id):
        if not cart_id:
            return {'message': 'Missing card id'}, 500
        else:
            return Cart.delete(cart_id)

    @jwt_required
    def post(self):
        data = request.get_json()
        current_user = User.find_by_username(get_jwt_identity())
        print(data)

        if not current_user:
          return {'message': 'User {} not found'}

        cart = Cart(current_user.id, data['items'])
        return 'Done', 200


class ProductFootprint(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_at', help = 'This field cannot be blank', required = True)
        parser.add_argument('end_at', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        print(data)
        current_user = User.find_by_username(get_jwt_identity())

        if not current_user:
          return {'message': 'User {} not found'}

        carts = ItemCart.get_footprint(current_user.id, data['start_at'], data['end_at'])
        food = { 'foods': list(map(lambda c: {'name': c[2], 'foot_print': c[3] }, carts))}

        return food




class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }
