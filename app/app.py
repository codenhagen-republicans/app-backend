#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api
import views, resources, models

app = Flask(__name__)
db = models.init_db(app)
api = Api(app)


app.config['SECRET_KEY'] = 'some-secret-string'


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')

app.run(debug=True)
