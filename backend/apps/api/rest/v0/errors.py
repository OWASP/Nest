from http import HTTPStatus
from rest_framework.response import Response
PROJECT_NOT_FOUND_MSG="Project not found"
CHAPTER_NOT_FOUND_MSG="Chapter not found"
EVENT_NOT_FOUND_MSG="Event not found"
def error_response(message,status):
    return Response({"message": message},status=status)
def project_not_found():
    return error_response(PROJECT_NOT_FOUND_MSG,status=404)
def chapter_not_found():
    return error_response(CHAPTER_NOT_FOUND_MSG,status=404)
def event_not_found():
    return error_response(EVENT_NOT_FOUND_MSG,status=404)
