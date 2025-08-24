import django_filters as filters
from common_bases.base_filters import GenericSearchFilterMixin
from django_filters.rest_framework import FilterSet


class GeneratedSourceFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedPollOfficeFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVoteFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVoteProposedFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVoterFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVoteVerifiedFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVoteAcceptedFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedCandidatePartyFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVotingPaperResultFilterSet(GenericSearchFilterMixin, FilterSet):

    pass


class GeneratedVotingPaperResultProposedFilterSet(
    GenericSearchFilterMixin, FilterSet
):

    pass


class GeneratedSourceTokenFilterSet(GenericSearchFilterMixin, FilterSet):

    pass
