from rest_framework.request import Request

from ...models import Source


class GeneratedSourceServices:

    @classmethod
    def pre_create_source(
        cls,
        request: Request,
        obj: None,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_create_source(
        cls,
        request: Request,
        instance: None,
        returned_obj: Source,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_update_source(
        cls,
        request: Request,
        obj: Source,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_update_source(
        cls,
        request: Request,
        instance: Source,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_partial_update_source(
        cls,
        request: Request,
        obj: Source,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_partial_update_source(
        cls,
        request: Request,
        instance: Source,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_delete_source(
        cls,
        request: Request,
        obj: Source,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_delete_source(
        cls,
        request: Request,
        instance: Source,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass
