#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from flask import Flask
import views, models, resources


app = Flask(__name__)

app.add_url_rule('/', views.index)

app.run(debug=True)
