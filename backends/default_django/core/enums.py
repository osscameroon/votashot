from .gen.enums import GeneratedAge, GeneratedGender, GeneratedSourceType


class SourceType(GeneratedSourceType):

    pass


class Gender(GeneratedGender):

    @classmethod
    def values(cls):
        return ["male", "female", "undecided"]


class Age(GeneratedAge):

    @classmethod
    def values(cls):
        return ["less_30", "less_60", "more_60", "undecided"]
