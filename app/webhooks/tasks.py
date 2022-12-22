import datetime
import pytz
from flask import request, jsonify, make_response
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only

from app.database import db_session
from app.logger import webhooks_logger as logger
from app.models import Task, Category
from app.request_models.task import TaskCreateRequest
from app.webhooks.check_request import request_to_context
from app.webhooks.check_webhooks_token import check_webhooks_token

from bot.charity_bot import dispatcher
from bot.formatter import display_task_notification
from bot.messages import TelegramNotification, SendUserMessageContext, SendUserNotificationsContext


class CreateTasks(MethodResource, Resource):
    method_decorators = {'post': [check_webhooks_token]}

    @doc(description='Сreates tasks in the database',
         tags=['Create tasks'],
         responses={
             200: {'description': 'ok'},
             400: {'description': 'error message'},
             403: {'description': 'Access is denied'}
         },
         params={'token': {
             'description': 'webhooks token',
             'in': 'header',
             'type': 'string',
             'required': True
         }},
         )
    def post(self):
        tasks = request_to_context(TaskCreateRequest, request)

        tasks_dict = {task.id: task for task in tasks}
        tasks_db = Task.query.options(load_only('archive')).all()
        task_id_json = [task.id for task in tasks]
        task_id_db = [task.id for task in tasks_db]

        task_to_send = []

        task_id_db_not_archive = [task.id for task in tasks_db if task.archive is False]
        task_for_archive = list(set(task_id_db_not_archive) - set(task_id_json))
        archive_records = [task for task in tasks_db if task.id in task_for_archive]
        archived_tasks = self.__archive_tasks(archive_records)

        task_id_db_archive = list(set(task_id_db) - set(task_id_db_not_archive))
        task_for_unarchive = list(set(task_id_db_archive) & set(task_id_json))
        unarchive_records = [task for task in tasks_db if task.id in task_for_unarchive]
        unarchived_tasks = self.__unarchive_tasks(unarchive_records, task_to_send, tasks_dict)

        task_for_adding_db = list(set(task_id_json) - set(task_id_db))
        tasks_to_add = [task for task in tasks if task.id in task_for_adding_db]
        added_tasks = self.__add_tasks(tasks_to_add, task_to_send)

        task_id_db_active = list(
            set(task_id_json) - set(task_for_archive) - set(task_for_unarchive) - set(task_for_adding_db)
        )
        active_tasks = [task for task in tasks_db if task.id in task_id_db_active]       
        updated_tasks = self.__update_active_tasks(active_tasks, task_to_send, tasks_dict)

        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Tasks: database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message='Bad request'), 400)
        logger.info(f'Tasks: Tasks to send - {task_to_send}')

        self.preparing_tasks_for_send(task_to_send)

        logger.info('Tasks: New tasks received')
        logger.info('——————————————————————————————————————————————————————')
        return make_response(jsonify(added_tasks=added_tasks,
                                     archived_tasks=archived_tasks,
                                     unarchived_tasks=unarchived_tasks,
                                     updated_tasks=updated_tasks), 200)

    def preparing_tasks_for_send(self, task_to_send):
        if not task_to_send:
            logger.info('Tasks: No tasks to send')
            return

        logger.info(
            f'Tasks: Tasks passed to the preparing_tasks_for_send method - {[(task.id, task.title) for task in task_to_send]}'
        )
        notification = TelegramNotification()

        send_time = datetime.datetime.now(pytz.utc)
        for task in task_to_send:
            category_id = task.category_id
            users = Category.query.filter_by(id=category_id).first().users
            logger.info(
                f'Tasks: Users with a subscription to {category_id} category in DB - {[user.telegram_id for user in users]}'
            )
            message = display_task_notification(task)
            user_notification_context = SendUserNotificationsContext([])
            for user in users:
                if user.has_mailing:
                    user_message_context = SendUserMessageContext(message=message, telegram_id=user.telegram_id)
                    user_notification_context.user_message_context.append(user_message_context)
            logger.info(
                f"Tasks: User's mailing list - {[user_message_context.telegram_id for user_message_context in user_notification_context.user_message_context]}"
            )
            if len(user_notification_context.user_message_context) != 0:
                dispatcher.job_queue.run_once(notification.send_batch_messages,
                                              send_time,
                                              context=user_notification_context,
                                              name=f'Sending: {message[0:10]}')

                logger.info(f'Tasks: submitting task: {task.id} {task.title}')
            # Adds a 10 second delay before processing the next task
            send_time = send_time + datetime.timedelta(seconds=10)

    def __add_tasks(self, tasks_to_add, task_to_send):
        task_ids = [task.id for task in tasks_to_add]
        for task in tasks_to_add:
            new_task = Task(
                id=task.id,
                title=task.title,
                name_organization=task.name_organization,
                deadline=task.deadline,
                category_id=task.category_id,
                bonus=task.bonus,
                location=task.location,
                link=task.link,
                description=task.description
                )
            new_task.archive = False
            db_session.add(new_task)
            task_to_send.append(new_task)
        logger.info(f'Tasks: Added {len(tasks_to_add)} new tasks.')
        logger.info(f'Tasks: Added task IDs: {task_ids}')
        return task_ids

    def __archive_tasks(self, archive_records):
        task_ids = [task.id for task in archive_records]
        for task in archive_records:
            task.archive = True
        logger.info(f'Tasks: Archived {len(archive_records)} tasks.')
        logger.info(f'Tasks: Archived task ids: {task_ids}')
        return task_ids

    def __unarchive_tasks(self, unarchive_records, task_to_send, tasks_dict):
        task_ids = [task.id for task in unarchive_records]
        for task in unarchive_records:
            task_from_dict = tasks_dict.get(task.id)
            self.__update_task_fields(task, task_from_dict)
            task_to_send.append(task)
        logger.info(f'Tasks: Unarchived {len(unarchive_records)} tasks.')
        logger.info(f'Tasks: Unarchived task IDs: {task_ids}')
        return task_ids

    def __hash__(self, task):
        if type(task) == dict:
            title = task.get('title')
            description = task.get('description')
            deadline = task.get('deadline')
            return hash(f'{title}{description}{deadline}')
        return hash(f'{task.title}{task.description}{task.deadline}')

    def __update_active_tasks(self, active_tasks, task_to_send, tasks_dict):
        updated_task_ids = []
        for task in active_tasks:
            task_from_dict = tasks_dict.get(task.id)
            if self.__hash__(task) != self.__hash__(task_from_dict):
                self.__update_task_fields(task, task_from_dict)
                task_to_send.append(task)
                updated_task_ids.append(task.id)
        logger.info(f'Tasks: Updated {len(updated_task_ids)} active tasks.')
        logger.info(f'Tasks: Updated active task ids: {updated_task_ids}')
        return updated_task_ids

    def __update_task_fields(self, task, task_from_dict):
        task.title = task_from_dict.title
        task.name_organization = task_from_dict.name_organization
        task.category_id = task_from_dict.category_id
        task.bonus = task_from_dict.bonus
        task.location = task_from_dict.location
        task.link = task_from_dict.link
        task.description = task_from_dict.description
        task.deadline = task_from_dict.deadline
        task.archive = False
