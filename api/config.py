import os
from datetime import timedelta


class BaseConfig():
    GOREST_API_ENDPOINT = 'https://gorest.co.in/public/v2'
    GO_REST_EXCEL_FILENAME = 'goRest_data.xlsx'
    GO_REST_BUCKETNAME = 'zappa-aj174h1ci'
    STORE_NAME = 'myLastCreator'


class EntityConfig():
    USERS = 'users'
    POSTS = 'posts'
    COMMENTS = 'comments'
    TODOS = 'todos'


class HttpStatusCode():
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    UNAUTHORIZE = 401
    INTERNAL_ERROR = 500
    NOT_FOUND = 404
    CONFLICT = 409
    FORBIDDEN = 403
    BAD_REQUEST = 400
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
