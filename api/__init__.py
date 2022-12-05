import json

from flask import Flask
from flask_cors import CORS

from .routes import rest_api

app = Flask(__name__)

app.config.from_object('api.config.BaseConfig')

rest_api.init_app(app)
CORS(app)

# """
#    Custom responses
# """

# @app.after_request
# def after_request(response):
#     """
#        Sends back a custom error with format
#     """

#     if int(response.status_code) == 404:
#             response_data = {"data": None,"statusCode":404,"message":"Endpoint not exist"}
#             response.set_data(json.dumps(response_data))
#             response.headers.add('Content-Type', 'application/json')
#     return response
