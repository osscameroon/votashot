from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import BaseFilterBackend


class ExpandingFilter(BaseFilterBackend):
    # The URL query parameter used for the ordering.
    ordering_param = "expand"
    ordering_fields = None
    ordering_title = _("Expanding")
    ordering_description = _(
        "Which fields to use when expanding the nested serializers in the results, separated by a comma (,)"
    )
    template = "rest_framework/filters/ordering.html"

    def get_schema_fields(self, view):
        assert (
            coreapi is not None
        ), "coreapi must be installed to use `get_schema_fields()`"
        assert (
            coreschema is not None
        ), "coreschema must be installed to use `get_schema_fields()`"
        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location="query",
                schema=coreschema.String(
                    title=force_str(self.ordering_title),
                    description=force_str(self.ordering_description),
                ),
            ),
            coreapi.Field(
                name="only",
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Return specific fields",
                    description="Return only a subset of fields instead of all the fields defined separated by comma (,)",
                ),
            ),
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.ordering_param,
                "required": False,
                "in": "query",
                "description": force_str(self.ordering_description),
                "schema": {
                    "type": "string",
                },
            },
            {
                "name": "only",
                "required": False,
                "in": "query",
                "description": "Return only a subset of fields instead of all the fields defined",
                "schema": {
                    "type": "string",
                },
            },
        ]

    def filter_queryset(self, request, queryset, view):
        return queryset
