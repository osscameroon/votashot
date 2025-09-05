from common_bases.enums import SimpleEnum


class GeneratedSourceType(SimpleEnum):

    OFFICIAL: str = "official"
    POLITICAL_PARTY: str = "political_party"
    INDEPENDANT: str = "independant"
    UNVERIFIED: str = "unverified"


class GeneratedGender(SimpleEnum):

    MALE: str = "male"
    FEMALE: str = "female"
    UNDECIDED: str = "undecided"


class GeneratedAge(SimpleEnum):

    LESS_30: str = "less_30"
    LESS_60: str = "less_60"
    MORE_60: str = "more_60"
    UNDECIDED: str = "undecided"
