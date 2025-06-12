from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as default_exception_handler
from rest_framework.response import Response


def exception_handler(exc, context):
    if isinstance(exc, APIException):
        details = exc.get_full_details()
        if isinstance(details, list):
            # sometimes it's a list?
            details = details[-1]
        details['result'] = details['code']
        del details['code']
        return Response(details, status=exc.status_code)

    return default_exception_handler(exc, context)


class ConfigError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
