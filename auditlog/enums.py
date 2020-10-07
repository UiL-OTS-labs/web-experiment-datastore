from enum import Enum


class Event(Enum):
    UNCATEGORISED = 'uncategorised'
    DOWNLOAD_DATA = 'download_data'
    VIEW_DATA = 'view_data'
    VIEW_SENSITIVE_DATA = 'view_sensitive_data'
    DELETE_DATA = 'delete_data'
    MODIFY_DATA = 'modify_data'
    ADD_DATA = 'add_data'


class UserType(Enum):
    SYSTEM = 'system'
    ADMIN = 'admin'
    RESEARCHER = 'researcher'
    UNKNOWN = 'unknown'
