class SimpleEnum:
    @classmethod
    def choices(cls):
        """Get choices as a tuple of tuple

        :return:
        """
        res = []
        for att in cls.__dict__.keys():
            if att.isupper():
                value = cls.__dict__[att]
                display = cls.get_display_name(att)
                res.append((value, display))

        if res:
            return res

        if len(cls.__bases__) > 0:
            base_cls = cls.__bases__[0]
            for att in base_cls.__dict__.keys():
                if att.isupper():
                    value = base_cls.__dict__[att]
                    display = base_cls.get_display_name(att, parent_cls=cls)
                    res.append((value, display))
        return res

    @classmethod
    def get_display_name(cls, att_name, parent_cls=None):
        """Get display name of an attribute

        :param app_name:
        :return:
        """
        r = cls.__dict__.get(f"_{cls.__name__}__{att_name}")
        if not r:
            if parent_cls:
                r = parent_cls.__dict__.get(f"_{parent_cls.__name__}__{att_name}")
        if not r:
            r = att_name

        return r

    @classmethod
    def values(cls):
        res = []
        for att in cls.__dict__.keys():
            if att.isupper():
                value = cls.__dict__[att]
                res.append(value)

        if res:
            return res

        if len(cls.__bases__) > 0:
            base_cls = cls.__bases__[0]
            for att in base_cls.__dict__.keys():
                if att.isupper():
                    value = base_cls.__dict__[att]
                    res.append(value)
        return res