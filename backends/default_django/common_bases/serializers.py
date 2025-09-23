from rest_framework.serializers import (
    CharField,
    IntegerField,
    JSONField,
    Serializer,
)


class EmptySerializer(Serializer):
    class Meta:
        ref_name = None


class BadRequestResponseSerializer(Serializer):
    message = CharField()
    code = CharField()
    data = JSONField()  # type: ignore

    class Meta:
        ref_name = None


class NotFoundResponseSerializer(Serializer):
    message = CharField()
    model = CharField()
    data = JSONField()  # type: ignore

    class Meta:
        ref_name = None


class CommonMetadataListSerialzer(Serializer):
    total_elements = IntegerField()
    total_pages = IntegerField()
    current_page = IntegerField()
    next_page = IntegerField()
    previous_page = IntegerField()

    class Meta:
        ref_name = None


class CommonListSerializer(Serializer):
    metadata = CommonMetadataListSerialzer()

    class Meta:
        ref_name = None
