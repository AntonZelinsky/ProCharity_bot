from app.models import User, Statistics
from app.database import db_session
from datetime import datetime
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from flask_restful import Resource
from sqlalchemy import func
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required


class Analysis(MethodResource, Resource):
    @doc(description='Analysis statistics',
         tags=['Analysis']
         )
    #@jwt_required()
    def get(self):
        added_users = db_session.query(func.date(User.date_registration), func.count(User.date_registration)).group_by(func.date(User.date_registration)).all()
        users = db_session.query(User.has_mailing).all()
        num_users = len(users)
        active_users = 0
        for user in users:
            if user['has_mailing']:
                active_users += 1
        deactivated_users = num_users - active_users
        command_stats = db_session.query(
            Statistics.command,
            func.count(Statistics.command)
        ).group_by(Statistics.command).all()
        added_users = [[d.strftime("%d %B, %Y"), n] for d, n, in added_users]
        return make_response(jsonify(added_users=dict(added_users),
                                     active_users=active_users,
                                     deactivated_users=deactivated_users,
                                     command_stats=dict(command_stats)), 200)
