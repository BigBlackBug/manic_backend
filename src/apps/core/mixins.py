from collections import OrderedDict


class FilterEmptyFieldsMixin:
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret = OrderedDict(list(filter(lambda x: x[1], ret.items())))
        return ret
