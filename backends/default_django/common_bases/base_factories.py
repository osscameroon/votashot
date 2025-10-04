from random import randint
from typing import Any, Dict, Type

from django.db.models.fields.related import (
    ForeignKey,
    ManyToManyField,
    OneToOneField,
)
from factory import Factory as OldFactory
from factory.base import StubObject
from factory.django import DjangoModelFactory as OldDjangoModelFactory
from model_bakery import baker
from rest_framework.serializers import ModelSerializer
from traceback_with_variables import activate_by_import


def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
    stub_dict = stub.__dict__
    for key, value in stub_dict.items():
        if isinstance(value, StubObject):
            stub_dict[key] = convert_dict_from_stub(value)
    return stub_dict


class Factory(OldFactory):
    @classmethod
    def data(cls, **kwargs) -> Dict:
        stub = cls.stub(**kwargs)
        return convert_dict_from_stub(stub)


class DjangoModelFactory(OldDjangoModelFactory):
    @classmethod
    def data(cls, **kwargs) -> Dict:
        stub = cls.stub(**kwargs)
        return convert_dict_from_stub(stub)


class AllFieldsSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"


def instance_to_dict(instance, many=False, fields_overrides=None,
                     serializer=None) -> dict:
    if serializer:
        serializer.instance = instance
        return serializer.data
    else:
        _model = instance.__class__
        if fields_overrides is None:
            fields_overrides = {}
        new_seria_cls: Type[AllFieldsSerializer] = type(
            f"{_model.__name__}OnFlySerializer",
            (AllFieldsSerializer,),
            fields_overrides,
        )
        new_seria_cls.Meta.model = _model
        new_seria_cls.Meta.fields = "__all__"
        seria = new_seria_cls(instance, many=many)
        return seria.data


def get_data_from_baker(_model, _save=False, _fields_overrides=None,
                        serializer=None, **kwargs):
    rel_data = {}

    for field in _model._meta.get_fields():
        f_name = field.name
        if f_name in kwargs and isinstance(kwargs[f_name], dict):
            continue

        if isinstance(field, (ForeignKey, OneToOneField)):
            rel_kwargs = kwargs.pop(f_name, {})
            rel_fields_ov = (
                _fields_overrides.pop(f_name, None)
                if _fields_overrides
                else None
            )
            rel_instance = baker.make(field.related_model, **rel_kwargs)
            rel_data[f"{f_name}_id"] = rel_instance.id
            rel_data[f"{f_name}_pk"] = rel_instance.pk
            rel_data[f_name] = instance_to_dict(
                rel_instance, fields_overrides=rel_fields_ov,
                serializer=getattr(serializer, f_name, None)
            )
        elif isinstance(field, ManyToManyField):
            rel_kwargs = kwargs.pop(f_name, {})
            rel_fields_ov = (
                _fields_overrides.pop(f_name, None)
                if _fields_overrides
                else None
            )
            _rel_qty = rel_kwargs.get("_quantity")
            if not _rel_qty:
                _rel_qty = randint(1, 10)
            rel_instance = baker.make(
                field.related_model, _quantity=_rel_qty, **rel_kwargs
            )
            rel_data[f_name] = instance_to_dict(
                rel_instance, many=True, fields_overrides=rel_fields_ov,
                serializer=getattr(serializer, f_name, None)
            )

    if _save:
        instance = baker.make(_model, **kwargs)
    else:
        instance = baker.prepare(_model, **kwargs)
    data = instance_to_dict(instance, fields_overrides=_fields_overrides, serializer=serializer)
    data.update(rel_data)

    return data
