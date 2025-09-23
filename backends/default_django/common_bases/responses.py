from beartype.typing import Union

from django.conf import settings
from rest_framework.response import Response


class CreatedResponse(Response):
    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        if isinstance(data, dict):
            new_data = data
        else:
            new_data = {"data": data}
        super().__init__(
            new_data, 201, template_name, headers, exception, content_type
        )


class GoodResponse(Response):
    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        if isinstance(data, dict):
            new_data = data
        else:
            new_data = {"data": data}
        super().__init__(
            new_data, status, template_name, headers, exception, content_type
        )


class DeletedResponse(Response):
    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        if isinstance(data, dict):
            new_data = data
        else:
            new_data = {"data": data}
        super().__init__(
            new_data, 204, template_name, headers, exception, content_type
        )


class BadRequestResponse(Response):
    def __init__(
        self,
        message: str,
        code: str,
        errors: Union[list, dict],
        status=400,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        request=None,
    ):
        new_data = {"message": message, "code": code, "errors": errors}
        if settings.DEBUG:
            try:
                new_data["sent_data"] = request.data
            except Exception:
                new_data["send_data"] = "<<ERROR>>"
        super().__init__(
            new_data, status, template_name, headers, exception, content_type
        )


class NotFoundResponse(Response):
    def __init__(
        self,
        message,
        model,
        data={},
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        request=None,
    ):
        if settings.DEBUG:
            data["sent_data"] = request.data
        new_data = {"message": message, "model": model, "data": data}
        super().__init__(
            new_data, 404, template_name, headers, exception, content_type
        )
