from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        response.data = {
            "success": False,
            "message": "Request failed",
            "data": {},
            "errors": errors,
        }

    return response
