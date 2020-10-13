"""Provides audit logging support to the application.

Audit logging is the practice of logging the actions of the users of the
application for legal reasons. If nothing happens, the log is redundant.
However, in case of data leaks and such it's an invaluable tool to track down
the people who could've created the leak.

This implementation can be seen as overly paranoid. It was originally written
for an application that processes very sensitive information.

Django should be configured to route all auditlog related stuff to a separate
database.
"""