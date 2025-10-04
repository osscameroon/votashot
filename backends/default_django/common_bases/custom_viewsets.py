import logging
from functools import lru_cache
from importlib import import_module

from beartype.typing import List, Optional, Union
from django.conf import settings
from django.core.exceptions import ValidationError as DjValidationError
from django.db.models import Model
from django.forms import Form, ModelForm
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from rest_framework.fields import empty
from rest_framework.renderers import (
    BaseRenderer,
    BrowsableAPIRenderer,
    JSONRenderer,
    TemplateHTMLRenderer,
)
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer, ModelSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from traceback_with_variables import format_exc
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, ButtonHolder, Layout
from django.utils.translation import gettext as _
from rest_framework.routers import SimpleRouter
from django.urls import reverse
from django.forms import modelform_factory

logger = logging.getLogger()


class CustomForm(Form):
    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        field_order=None,
        use_required_attribute=None,
        renderer=None,
        **kwargs,
    ):
        super().__init__(
            data=data,
            files=files,
            auto_id=auto_id,
            prefix=prefix,
            initial=initial,
            error_class=error_class,
            label_suffix=label_suffix,
            empty_permitted=empty_permitted,
            field_order=field_order,
            use_required_attribute=use_required_attribute,
            renderer=renderer,
        )
        self.kwargs = kwargs
        self.validation_error_class = DjValidationError


class CustomModelForm(ModelForm):
    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None,
        **kwargs,
    ):
        super().__init__(
            data=data,
            files=files,
            auto_id=auto_id,
            prefix=prefix,
            initial=initial,
            error_class=error_class,
            label_suffix=label_suffix,
            empty_permitted=empty_permitted,
            instance=instance,
            use_required_attribute=use_required_attribute,
            renderer=renderer,
        )
        self.kwargs = kwargs
        self.validation_error_class = DjValidationError


class CustomGenericViewSet(GenericViewSet):
    form_class: Optional[Union[CustomForm, CustomModelForm]] = None
    pre_services = {}
    post_services = {}

    create_success_url: Optional[str] = None
    update_success_url: Optional[str] = None
    delete_success_url: Optional[str] = None
    create_template: Optional[str] = None
    update_template: Optional[str] = None
    delete_template: Optional[str] = None

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(format_exc(e))
            return self.finalize_response(
                request, self.smart_response(exception=e, status=400)
            )

    def smart_response(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=None,
        content_type=None,
        htmx_redirect=None,
    ):
        if isinstance(exception, Exception):
            err_msg = getattr(exception, "message", None)
            err_code = getattr(exception, "code", "unknown")
            status = getattr(exception, "status", None) or status
            errors = getattr(exception, "errors", None)
            template_name = (
                getattr(exception, "template_name", None) or template_name
            )
            if not err_msg:
                err_msg = str(exception)
            data = {"code": err_code, "message": err_msg, "errors": errors}
            if settings.DEBUG:
                data["traceback"] = format_exc(exception)

        if htmx_redirect:
            headers = headers if headers else {}
            headers["HX-Redirect"] = htmx_redirect

        return Response(
            data=data,
            status=status,
            template_name=template_name,
            headers=headers,
            content_type=content_type,
            exception=False,
        )

    def smart_error(
        self,
        message,
        code,
        errors=None,
        status=400,
        template_name=None,
        headers=None,
        content_type=None,
        context=None,
    ):
        data = {"code": code, "message": message, "errors": errors}
        if context and self.request.accepted_renderer.format == "html":
            data.update(context)

        return Response(
            data=data,
            status=status
            if self.request.accepted_renderer.format != "html"
            else 200,
            template_name=template_name,
            headers=headers,
            content_type=content_type,
            exception=False,
        )

    def get_smart_serializer(
        self, serializer_class=None, form_class=None, args=None, kwargs=None
    ):
        args = args if args else []
        kwargs = kwargs if kwargs else {}
        serializer_class = (
            serializer_class if serializer_class else self.serializer_class
        )
        form_class = form_class if form_class else self.form_class

        context = (
            kwargs.pop("context", None) or self.get_serializer_context() or {}
        )
        context.setdefault("request", self.request)

        if (
            self.request.accepted_renderer.format == "json"
            and serializer_class
        ):
            return serializer_class(*args, **kwargs, context=context)
        elif self.request.accepted_renderer.format == "html" and form_class:
            return form_class(*args, **kwargs, context=context)
        else:
            raise ValueError(
                f"{self.request.accepted_renderer.media_type} {self.request.accepted_renderer.format} not supported"
            )

    def get_renderers(self) -> List[BaseRenderer]:
        if getattr(self.request, "htmx", None):
            return [TemplateHTMLRenderer(), BrowsableAPIRenderer()]
        else:
            return [JSONRenderer(), BrowsableAPIRenderer()]

    def is_html_renderer(self):
        return self.request.accepted_renderer.format == "html"

    def post_action_service(
        self,
        action: str,
        request,
        instance: Optional[Model],
        returned_obj: Optional[Model],
    ):
        services = self.post_services.get(action)
        if not isinstance(services, list):
            services = [services]
        for service in services:
            if callable(service):
                service(request, instance, returned_obj)

    def pre_action_service(
        self, action: str, request, instance: Optional[Model]
    ):
        services = self.pre_services.get(action)
        if not isinstance(services, list):
            services = [services]
        for service in services:
            if callable(service):
                service(request, instance)

    def generic_custom_action_handler(
        self,
        request,
        action: str,
        detail: bool,
        serializer_class,
        form_class=None,
        many=False,
        pass_instance_as=None,
        return_instance_data=True,
        success_status=200,
    ):
        if detail:
            instance = self.get_object()
        else:
            instance = None

        rcv_ser = self.get_smart_serializer(
            serializer_class=serializer_class,
            form_class=form_class,
            kwargs={"data": self.request.data, "many": many},
        )

        if rcv_ser.is_valid():
            self.pre_action_service(action, request, instance)

            save_kwargs = {}
            if pass_instance_as:
                save_kwargs[pass_instance_as] = instance
            returned_obj = rcv_ser.save(**save_kwargs)

            self.post_action_service(action, request, instance, returned_obj)
            headers = self.get_success_headers(rcv_ser.data)

            if return_instance_data:
                instance.refresh_from_db()
                ret_data = self.serializer_class(instance=instance).data
            else:
                ret_data = rcv_ser.data

            return self.smart_response(
                ret_data,
                template_name="components/empty.html",
                status=204 if self.is_html_renderer() else success_status,
                htmx_redirect=self.create_success_url,
                headers=headers,
            )
        else:
            return self.smart_error(
                "Unable to create",
                "create_error",
                rcv_ser.errors,
                template_name=self.create_template,
                context={"form": rcv_ser},
            )

    @lru_cache(maxsize=None)
    def get_object(self):
        """We re-implement it as a cached property to avoid calling each time"""
        return super().get_object()


class ExpandableModelSerializer(ModelSerializer):

    expandable_fields = {}

    def __init__(self, instance=None, data=empty, ignore=None, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)
        self._ignore = ignore or []

    @cached_property
    def fields(self):
        old_fields = super().fields

        for fl_name in self._ignore:
            old_fields.pop(fl_name, None)

        if "request" not in self.context:
            return old_fields

        # we avoid propagating the expand and only logic to nested serializers.
        current_class = self.__class__
        # we allow recursive nesting
        if isinstance(self.parent, current_class):
            pass
        # we allow being present in a list
        elif (
            isinstance(self.parent, ListSerializer)
            and self.parent.child.__class__ == current_class
        ):
            pass
        else:
            return old_fields

        only = [
            field.strip()
            for field in self.context["request"].GET.get("only", "").split(",")
            if field
        ]
        if only:
            allowed = set(only)
            existing = set(old_fields.keys())
            for field_name in existing - allowed:
                old_fields.pop(field_name)

        to_expand = [
            field.strip()
            for field in self.context["request"]
            .GET.get("expand", "")
            .split(",")
            if field
        ]
        for fl_name in to_expand:
            if fl_name not in self.expandable_fields:
                raise ValueError(
                    f"{fl_name} is not present in the expandable fields. "
                    f"Available fields are: {list(self.expandable_fields.keys())}"
                )
            else:
                fl_value = self.expandable_fields[fl_name]
                if isinstance(fl_value, dict):
                    serializer_name = fl_value.pop("serializer")
                    serializer = self.__get_refered_serializer(
                        serializer_name
                    )(**fl_value)
                    fl_value = serializer

                old_fields[fl_name] = fl_value

        return old_fields

    def __get_refered_serializer(self, serializer_name: str):
        module_name = self.__class__.__module__
        module = import_module(module_name)
        serializer_cls = getattr(module, serializer_name, None)
        if not serializer_cls:
            module_name, serializer_name = serializer_name.rsplit(
                ".", maxsplit=1
            )
            module = import_module(module_name)
            serializer_cls = getattr(module, serializer_name, None)

        if not serializer_cls:
            raise ValueError(f"Can't find a serializer: {serializer_name}")

        return serializer_cls


class CustomGenericDashboardViewSet(GenericViewSet):
    authentication_classes = [SessionAuthentication]
    renderer_classes = [TemplateHTMLRenderer]
    schema = None

    template_list_name: str = 'common_bases/dashboard/generic_list.html'
    template_create_name: str = 'common_bases/dashboard/generic_edit.html'
    template_update_name: str = template_create_name
    url_basename:str = None
    form_class = None
    model = None
    model_display_name = None
    model_display_name_plural = None
    url_namespace: str = 'dashboard'

    form_class_fields = "__all__"
    form_class_exclude = None
    form_class_fields_callback = None
    form_class_widgets = None
    form_class_localized_fields = None
    form_class_labels = None
    form_class_help_texts = None
    form_class_error_messages = None
    form_class_field_classes = None

    table_display_columns = [('id', 'Id')]
    table_search_columns = []
    table_ordering_columns = []
    table_server_side_rendering = False

    pre_services = {}
    post_services = {}

    html_modal_size = "medium"
    side_add_button = True
    title_add_button = True

    _router = None

    @staticmethod
    def get_router() -> SimpleRouter:
        if CustomGenericDashboardViewSet._router:
            return CustomGenericDashboardViewSet._router
        else:
            CustomGenericDashboardViewSet._router = SimpleRouter()
            return CustomGenericDashboardViewSet._router

    def get_html_context(self):
        print(f"{self = }")
        return {'view': self, 'side_links': self.get_side_links()}

    def get_side_links(self):
        router = CustomGenericDashboardViewSet.get_router()
        return [
            {
                "display": viewset.get_model_display_name_plural(),
                "url_name": f"{viewset.namespaced_base_url()}-list",
                "is_active": self.__class__ == viewset,
                "add_button": viewset.side_add_button,
            }
            for prefix, viewset, basename in router.registry
        ]

    def get_form(self, **kwargs):
        if self.form_class:
            form_class = self.form_class
        else:
            form_class = modelform_factory(self.model,
                            fields=self.form_class_fields,
                            exclude=self.form_class_exclude,
                            formfield_callback=self.form_class_fields_callback,
                           widgets=self.form_class_widgets,
                           localized_fields=self.form_class_localized_fields,
                           labels=self.form_class_labels,
                           help_texts=self.form_class_help_texts,
                           error_messages=self.form_class_error_messages,
                           field_classes=self.form_class_field_classes)
        form = form_class(**kwargs, **self.get_form_kwargs())
        self.add_crispy_helper(form)
        return form

    def add_crispy_helper(self, form):
        if not getattr(form, 'helper', None):
            form.helper = FormHelper()
            form.helper.layout = form.helper.build_default_layout(form)

        form.helper.attrs.update({'up-submit':''})

        if form.instance.pk:
            form.helper.form_action = reverse(self.namespaced_base_url_prop + '-update',
                                         kwargs={'pk': form.instance.pk})
            buttons = [Submit('update', 'Update')]
        else:
            form.helper.form_action = reverse(self.namespaced_base_url_prop +'-list')
            buttons = [Submit('create', 'Create')]

        form.helper.layout.fields.append(ButtonHolder(*buttons))

        return form

    @classmethod
    def namespaced_base_url(cls):
        return f"{cls.url_namespace}:{cls.url_basename}"

    @property
    def namespaced_base_url_prop(self):
        return f"{self.url_namespace}:{self.url_basename}"

    def post_action_service(
        self,
        action: str,
        request,
        instance: Optional[Model],
        returned_obj: Optional[Model],
    ):
        services = self.post_services.get(action)
        if not isinstance(services, list):
            services = [services]
        for service in services:
            if callable(service):
                service(request, instance, returned_obj)

    def pre_action_service(
        self, action: str, request, instance: Optional[Model]
    ):
        services = self.pre_services.get(action)
        if not isinstance(services, list):
            services = [services]
        for service in services:
            if callable(service):
                service(request, instance)

    @classmethod
    def get_model_display_name(cls):
        if cls.model_display_name:
            return cls.model_display_name
        else:
            return _(cls.model.__name__)

    @classmethod
    def get_model_display_name_plural(cls):
        if cls.model_display_name_plural:
            return cls.model_display_name_plural
        else:
            return cls.get_model_display_name() + "s"

    @classmethod
    def get_side_display(cls):
        return cls.get_model_display_name_plural()

    def get_form_kwargs(self):
        return {}
