from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # DRF-raised errors (permission denial, auth failure, etc.) bypass our views
    # entirely and render as {"detail": "..."}. Reshape them here so every error
    # response, not just the ones we build by hand, matches {status, message}.
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict) and 'detail' in response.data:
        response.data = {
            'status': False,
            'message': response.data['detail'],
        }

    return response
