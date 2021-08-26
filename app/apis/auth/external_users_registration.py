from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only

from app.database import db_session
from app.models import ExternalSiteUser
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from app.logger import logger


class ExternalUserRegistration(MethodResource, Resource):

    @doc(description='Receives user data from the portal for further registration.', tags=['User Registration'])
    @use_kwargs(
        {'id': fields.Int(required=True),
         'id_hash': fields.Str(description='md5 hash of external_id', required=True),
         'first_name': fields.Str(required=True),
         'last_name': fields.Str(required=True),
         'email': fields.Str(required=True),
         'specializations': fields.Str(required=True)}
    )
    def post(self, **kwargs):
        external_id = kwargs.get('id')

        user = ExternalSiteUser.query.options(load_only('external_id')).filter_by(external_id=external_id).first()
        if user:
            user.first_name = kwargs.get('first_name')
            user.last_name = kwargs.get('last_name')
            user.specializations = kwargs.get('specializations')
            user.updated_date = datetime.now()

        else:
            user = ExternalSiteUser(
                external_id=external_id,
                external_id_hash=kwargs.get('id_hash'),
                first_name=kwargs.get('first_name'),
                last_name=kwargs.get('last_name'),
                email=kwargs.get('email'),
                specializations=kwargs.get('specializations'),
            )
            db_session.add(user)

        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'External users registration: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        logger.info(f'External users registration: The external user "{external_id}" successful registered.')
        return make_response(jsonify(message='successful'), 200)
