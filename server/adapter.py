import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from typing import Any, Dict, Optional

from base.database import Database
from base.utils import CustomJSONEncoder, snake_case


def adapt(
    f,
    *,
    post: bool = False,
    query_parameter: Optional[str] = None,
    database: bool = True
):
    """
    Converts a regular Python to a Django view for an HTTP JSON endpoint.
    """

    def wrapper(request: HttpRequest, **kwargs) -> HttpResponse:
        # Django passes parameters from the URL as keyword arguments, but we want to
        # pass them as positional arguments, so we convert them to a list here.
        #
        # This works as of Python 3.6, where keyword argument order is preserved.
        args = list(kwargs.values())

        if query_parameter:
            args.append(request.GET.get(query_parameter))

        # If a POST request, then parse the body of the request as UTF-8-encoded JSON
        # and pass the result as the last positional argument to the function.
        if post:
            payload = json.loads(request.body, encoding="utf8")
            payload = _convert_request_payload(payload)
            args.append(payload)

        with Database(readonly=not post) as db:
            if database:
                args = [db] + args

            return JsonResponse(f(*args), encoder=CustomJSONEncoder, safe=False)

    # Use a Django decorator to send an HTTP 4xx error if API endpoint is tried with the
    # wrong HTTP method.
    if post:
        wrapper = require_POST(wrapper)
    else:
        wrapper = require_GET(wrapper)

    return wrapper


def _convert_request_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts the JSON payload of a POST request to use snake-case keys.
    """
    return {snake_case(key): value for key, value in payload.items()}
