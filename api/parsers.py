from rest_framework.parsers import BaseParser


class PlainTextParser(BaseParser):
    """
    Plain text parser. As the name would suggest, it only reads in the data
    as a Python string.
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()
