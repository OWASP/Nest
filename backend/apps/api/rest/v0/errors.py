from http import HTTPStatus
from rest_framework.response import Response
PROJECT_NOT_FOUND_MSG="Project not found"
CHAPTER_NOT_FOUND_MSG="Chapter not found"
EVENT_NOT_FOUND_MSG="Event not found"
def error_response(message,status=HTTPStatus.NOT_FOUND):
    return Response({"message", message},status=status)
def project_not_found():
    return error_response(PROJECT_NOT_FOUND_MSG)
def chapter_not_found():
    return error_response(CHAPTER_NOT_FOUND_MSG)
def event_not_found():
    return error_response(EVENT_NOT_FOUND_MSG)
