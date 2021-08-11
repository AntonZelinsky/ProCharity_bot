from sqlalchemy.exc import SQLAlchemyError

from app.models import ReasonCanceling, User, Category, Task, Users_Categories, ExternalSiteUser
from app.database import db_session
from datetime import datetime
from sqlalchemy.orm import load_only
from sqlalchemy import select
from email_validator import validate_email, EmailNotValidError
from app.logger import bot_logger as logger


class UserDB:
    def add_user(self, telegram_user, external_id_hash):
        telegram_id = telegram_user.id
        username = telegram_user.username
        last_name = telegram_user.last_name
        first_name = telegram_user.first_name
        record_updated = False
        user = User.query.filter_by(telegram_id=telegram_id).first()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                date_registration=datetime.now(),
                first_name=first_name,
                last_name=last_name)
            db_session.add(user)

        if external_id_hash:
            external_user = ExternalSiteUser.query.filter_by(external_id_hash=external_id_hash[0]).first()

            if external_user:
                user.first_name = external_user.first_name
                user.last_name = external_user.last_name
                user.external_id = external_user.external_id
                user.email = external_user.email
                user.external_signup_date = external_user.created_date

                if external_user.specializations:
                    external_user_specializations = [int(x) for x in external_user.specializations.split(',')]
                    specializations = Category.query.filter(Category.id.in_(external_user_specializations)).all()

                    for specialization in specializations:
                        user.categories.append(specialization)

                db_session.delete(external_user)
                try:
                    db_session.commit()
                except SQLAlchemyError as ex:
                    logger.error(f"User DB - 'add_user' method: {str(ex)}")
                return user

        if user.username != username:
            user.username = username
            record_updated = True

        if not user.external_id:
            if user.last_name != last_name:
                user.last_name = last_name
                record_updated = True

            if user.first_name != first_name:
                user.first_name = first_name
                record_updated = True

        if record_updated:
            try:
                db_session.commit()
            except SQLAlchemyError as ex:
                logger.error(f"User DB - 'add_user' method: {str(ex)}")
        return user

    def check_user_category(telegram_id):
        user_categories = User.query.get(telegram_id).categories
        if not user_categories:
            return False
        return True


    def get_categories(self, telegram_id):
        """
        Returns a collection of categories. If the user has selected one of them, it returns True in dictionary.
        :param telegram_id: chat_id of current user
        :return:
        """
        result = []
        user_categories = [category.id for category in User.query.filter_by(telegram_id=telegram_id).first().categories]
        all_categories = Category.query.options(load_only('id')).filter_by(archive=False)
        for category in all_categories:
            category_view_model = {}
            category_view_model['category_id'] = category.id
            category_view_model['name'] = category.name
            if category.id in user_categories:
                category_view_model['user_selected'] = True
            else:
                category_view_model['user_selected'] = False
            result.append(category_view_model)
        return result

    def get_user_active_tasks(self, telegram_id, shown_task):
        users_categories_telegram_ids = db_session.query(Users_Categories.telegram_id).all()
        telegram_ids = [telegram_id[0] for telegram_id in users_categories_telegram_ids]
        if telegram_id in telegram_ids:
            db_query = select(Task, Category.name). \
                where(Users_Categories.telegram_id == telegram_id). \
                where(Task.archive == False).where(~Task.id.in_(shown_task)). \
                join(Users_Categories, Users_Categories.category_id == Task.category_id). \
                join(Category, Category.id == Users_Categories.category_id)
        else:
            db_query = select(Task, Category.name). \
                where(Task.archive == False).where(~Task.id.in_(shown_task)). \
                join(Category, Category.id == Task.category_id)
        result = db_session.execute(db_query)
        return [[task, category_name] for task, category_name in result]


    def change_subscription(self, telegram_id):
        """
        Update subscription status of user.
        :param telegram_id: Chat id of current user from the telegram update obj.
        :return:
        """
        user = User.query.options(load_only('has_mailing')).filter_by(telegram_id=telegram_id).first()

        if user.has_mailing:
            user.has_mailing = False
        else:
            user.has_mailing = True
        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f"User DB - 'change_subscription' method: {str(ex)}")

        return user.has_mailing

    def change_user_category(self, telegram_id, category_id):
        user = User.query.filter_by(telegram_id=telegram_id).first()
        category = Category.query.get(category_id)

        if category in user.categories:
            user.categories.remove(category)
            db_session.add(user)
        else:
            user.categories.append(category)
            db_session.add(user)
        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f"User DB - 'change_user_category' method: {str(ex)}")

    def cancel_feedback_stat(self, telegram_id, reason_canceling):
        reason = ReasonCanceling(
            telegram_id=telegram_id,
            reason_canceling=reason_canceling,
            added_date=datetime.now()
        )
        db_session.add(reason)
        try:
            return db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f"User DB - 'cancel_feedback_stat' method: {str(ex)}")

    def get_user(self, telegram_id):
        return User.query.get(telegram_id)

    def set_user_email(self, telegram_id, email):
        user = User.query.filter_by(telegram_id=telegram_id).first()
        try:
            validate_email(email)
            user.email = email
            db_session.commit()
            return True
        except EmailNotValidError as ex:
            logger.error(f"User DB - 'set_user_email' method: {str(ex)}")
            return False
