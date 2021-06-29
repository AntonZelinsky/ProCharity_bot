USERS_SCHEMA = {
    "200": {'description': 'ok',
            "examples": {
                'RESULT': {
                    "total": 100,
                    "pages": 10,
                    "next_page": 10,
                    "previous_page": 'null',
                    "next_url": "/api/v1/users/?page=2&limit=10",
                    "previous_url": 'null',
                    "result":
                        [
                            {"id": 'id',
                             "username": 'username',
                             "email": 'email@example.com',
                             "first_name": "First Name",
                             "last_name": "Last Name",
                             "telegram_id": 000000000,
                             "has_mailing": 'true',
                             "date_registration": "Sat, 26 Jun 2021 18:29:41 GMT"
                             }
                        ]
                }
            }
            }
}

