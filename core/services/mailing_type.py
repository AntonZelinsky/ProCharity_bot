from enum import Enum


class MailingType(Enum):
    """
    This class implements enumeration.
    """
    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBED = 'unsubscribed'
    ALL = 'all'
