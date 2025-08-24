from rest_framework.request import Request

from ...models import Vote


class GeneratedVoteServices:

    @classmethod
    def pre_create_vote(
        cls,
        request: Request,
        obj: None,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_create_vote(
        cls,
        request: Request,
        instance: None,
        returned_obj: Vote,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_update_vote(
        cls,
        request: Request,
        obj: Vote,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_update_vote(
        cls,
        request: Request,
        instance: Vote,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_partial_update_vote(
        cls,
        request: Request,
        obj: Vote,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_partial_update_vote(
        cls,
        request: Request,
        instance: Vote,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_delete_vote(
        cls,
        request: Request,
        obj: Vote,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_delete_vote(
        cls,
        request: Request,
        instance: Vote,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass
