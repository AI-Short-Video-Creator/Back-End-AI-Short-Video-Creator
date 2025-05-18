from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

bcrypt = Bcrypt()
jwt = JWTManager()
mongo = PyMongo()