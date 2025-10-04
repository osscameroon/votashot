import django_filters as filters
from django.db.models import Q

class GenericSearchFilterMixin:
    search = filters.CharFilter('id', method='just_search')
    search_fields = []

    def just_search(self, queryset, name, value):
        if not self.search_fields:
            return queryset

        search_fields = self.search_fields.copy()
        field = search_fields.pop()
        filt_value = Q(**{f'{field}__icontains': value})

        while len(search_fields):
            field = search_fields.pop()
            filt_value |= Q(**{f'{field}__icontains': value})

        return queryset.filter(filt_value)