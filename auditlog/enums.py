from enum import Enum


class Event(Enum):
    """Enum to describe the nature of the event"""
    UNCATEGORISED = 'uncategorised'
    DOWNLOAD_DATA = 'download_data'
    VIEW_DATA = 'view_data'
    VIEW_SENSITIVE_DATA = 'view_sensitive_data'
    DELETE_DATA = 'delete_data'
    MODIFY_DATA = 'modify_data'
    ADD_DATA = 'add_data'


class UserType(Enum):
    """Enum to describe the role of the user who created the event"""
    SYSTEM = 'system'  # Use only when the system takes an action on it's own.
    ADMIN = 'admin'
    RESEARCHER = 'researcher'
    UNKNOWN = 'unknown'  # Default value, should not be used by you!
