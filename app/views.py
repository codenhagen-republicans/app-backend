#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from flask import jsonify


def index():
    return jsonify({'message': 'Hello, World!'})
