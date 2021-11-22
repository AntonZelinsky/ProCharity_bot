import os
import re

from flask import send_file, request, jsonify, make_response
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app import config
from app.logger import app_logger as logger


class DownloadLogs(MethodResource, Resource):
    @doc(description='Download logs',
         tags=['Logs'],
         params={
             'log_file': {
                 'description': 'app_logs, bot_logs or webhook_logs',
                 'in': 'query',
                 'type': 'string',
                 'required': True},
             'Authorization': config.PARAM_HEADER_AUTH})     
    @jwt_required()
    def get(self):
        log_file = self.__check_file_name(request.args.get('log_file'))
        directory = f"../logs/{log_file}"
        try:
            return send_file(directory, as_attachment=True)
        except FileNotFoundError:
            logger.info(f'Download log files: incorrect file_name "{log_file}"')
            return 'Make sure you pass in the correct log_file'

    def __check_file_name(self, file_name):
        if file_name in re.findall(r'(?:app_logs|bot_logs|webhooks_logs)', file_name):
            return file_name
        return None


class GetListLogFiles(MethodResource, Resource):
    @doc(description='Get list of log files', 
         tags=['Logs'],
         params={
             'Authorization': config.PARAM_HEADER_AUTH})     
    @jwt_required()
    def get(self):
        log_files = os.listdir(path='./logs')
        return make_response(jsonify(log_files=log_files), 200)
