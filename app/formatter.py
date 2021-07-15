def get_user_information(user):
    return {
        'telegram_id': user.telegram_id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'external_id': user.external_id,
        'has_mailing': user.has_mailing,
        'date_registration': user.date_registration.strftime('%Y-%m-%d'),
    }
