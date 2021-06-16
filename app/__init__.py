from app.models import User
from app.database import db_session
from flask import Flask
from app.config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restful import Api

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
api = Api(app)
CORS(app)

from . import api, routers
