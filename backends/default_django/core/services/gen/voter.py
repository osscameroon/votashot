from rest_framework.request import Request

from ...models import Voter


class GeneratedVoterServices:

    @classmethod
    def pre_create_voter(
        cls,
        request: Request,
        obj: None,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_create_voter(
        cls,
        request: Request,
        instance: None,
        returned_obj: Voter,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_update_voter(
        cls,
        request: Request,
        obj: Voter,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_update_voter(
        cls,
        request: Request,
        instance: Voter,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_partial_update_voter(
        cls,
        request: Request,
        obj: Voter,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_partial_update_voter(
        cls,
        request: Request,
        instance: Voter,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def pre_delete_voter(
        cls,
        request: Request,
        obj: Voter,
        **kwargs,
    ):
        """"""
        pass

    @classmethod
    def post_delete_voter(
        cls,
        request: Request,
        instance: Voter,
        returned_obj,
        **kwargs,
    ):
        """"""
        pass
