from typing import Any

from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action


class CustomCreateModelMixin(CreateModelMixin):
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rcv_ser = self.get_smart_serializer(
            kwargs={"data": self.request.data},
        )
        if rcv_ser.is_valid():
            self.pre_action_service("create", request, None)
            returned_obj = rcv_ser.save()

            self.post_action_service("create", request, None, returned_obj)
            headers = self.get_success_headers(rcv_ser.data)

            return self.smart_response(
                rcv_ser.data,
                template_name="components/empty.html",
                status=204 if self.is_html_renderer() else 201,
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


class CustomNestedCreateModelMixin(CreateModelMixin):
    parent_kwarg_name = ""
    parent_model = None
    parent_model_filter_attribute = "id"
    serializer_kwarg_name = ""
    check_has_parent_perm = True

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rcv_ser = self.get_smart_serializer(
            kwargs={"data": self.request.data},
        )
        if rcv_ser.is_valid():
            self.pre_action_service("create", request, None)

            parent_instance = self.parent_model.objects.get(
                **{
                    self.parent_model_filter_attribute: self.kwargs[
                        self.parent_kwarg_name
                    ]
                }
            )
            if self.check_has_parent_perm:
                self.check_parent_permissions(parent_instance)

            returned_obj = rcv_ser.save(
                **{self.serializer_kwarg_name: parent_instance}
            )

            self.post_action_service("create", request, None, returned_obj)
            headers = self.get_success_headers(rcv_ser.data)

            return self.smart_response(
                rcv_ser.data,
                template_name="components/empty.html",
                status=204 if self.is_html_renderer() else 201,
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


class CustomUpdateModelMixin(UpdateModelMixin):
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        rcv_ser = self.get_smart_serializer(
            kwargs={
                "data": self.request.data,
                "instance": instance,
                "partial": partial,
            },
        )
        if rcv_ser.is_valid():
            self.pre_action_service(
                "partial_update" if partial else "update", request, instance
            )
            returned_obj = rcv_ser.save()

            self.post_action_service(
                "partial_update" if partial else "update",
                request,
                instance,
                returned_obj,
            )

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            rcv_ser.instance.refresh_from_db()

            return self.smart_response(
                rcv_ser.data,
                template_name="components/empty.html",
                status=204 if self.is_html_renderer() else 200,
                htmx_redirect=self.update_success_url,
            )
        else:
            return self.smart_error(
                "Unable to create",
                "create_error",
                rcv_ser.errors,
                template_name=self.update_template,
                context={"form": rcv_ser},
            )


class CustomDestroyModelMixin(DestroyModelMixin):
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        self.pre_action_service("delete", request, instance)
        instance.delete()
        self.post_action_service("delete", request, instance, None)

        return self.smart_response(
            {},
            template_name="components/empty.html",
            status=204
            if self.is_html_renderer()
            else status.HTTP_204_NO_CONTENT,
            htmx_redirect=self.delete_success_url,
        )


class CustomDashboardListModelMixin(ListModelMixin):

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.table_server_side_rendering:
            page = queryset
        else:
            page = self.paginate_queryset(queryset)
        ctx = self.get_html_context()
        ctx['object_list'] = page
        return Response(ctx, template_name=self.template_list_name)


class CustomDashboardRetrieveModelMixin(RetrieveModelMixin):

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ctx = self.get_html_context()
        ctx['object'] = instance
        form = self.get_form(instance=instance)
        ctx['form'] = form
        return Response(ctx, template_name=self.template_update_name)


class CustomDashboardCreateModelMixin(CreateModelMixin):

    def perform_create(self, form):
        return form.save()

    def create(self, request, *args, **kwargs) -> Response:
        form = self.get_form(data=self.request.data)
        ctx = self.get_html_context()

        if form.is_valid():
            self.pre_action_service("create", request, None)
            returned_obj = self.perform_create(form)
            print(f"{returned_obj = }")

            self.post_action_service("create", request, None, returned_obj)
            headers = {"X-Up-Events": f'[{{"type":"created", "id": {returned_obj.id}}}]',
                       "X-Up-Accept-Layer": "true"}

            return Response({}, headers=headers,
                            template_name="common_bases/dashboard/empty.html")
        else:
            ctx['form'] = form
            return Response(ctx, template_name=self.template_create_name,
                            status=422)

    @action(methods=['GET'], detail=False)
    def add(self, request, *args, **kwargs):
        ctx = self.get_html_context()
        form = self.get_form()
        ctx['form'] = form
        return Response(ctx, template_name=self.template_create_name)


class CustomDashboardUpdateModelMixin(UpdateModelMixin):

    def perform_update(self, form):
        return form.save()

    def update(self, request, *args, **kwargs) -> Response:
        partial = True
        instance = self.get_object()

        form = self.get_form(data=self.request.data, instance=instance)
        ctx = self.get_html_context()

        if form.is_valid():
            self.pre_action_service(
                "partial_update" if partial else "update", request, instance
            )
            returned_obj = self.perform_update(form)

            self.post_action_service(
                "partial_update" if partial else "update",
                request,
                instance,
                returned_obj,
            )
            headers = {"X-Up-Events": f'[{{"type":"updated", "id": {returned_obj.id}}}]',
                       "X-Up-Accept-Layer": "true"}
            return Response({}, headers=headers,
                            template_name="common_bases/dashboard/empty.html")
        else:
            ctx['form'] = form
            return Response(ctx, template_name=self.template_create_name,
                            status=422)

    @action(methods=['POST'], detail=True, url_path='update',
            url_name='update')
    def another_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CustomDashboardDestroyModelMixin:

    @action(methods=['POST', 'GET'], detail=True)
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.method.lower() == 'post':
            self.pre_action_service("delete", request, instance)
            self.perform_destroy(instance)
            self.post_action_service("delete", request, instance, None)

            headers = {"X-Up-Events": '["deleted"]',
                       "X-Up-Accept-Layer": "true"}

            return Response({}, headers=headers, status=204,
                            template_name="common_bases/dashboard/empty.html")
        else:
            return Response({'object': instance}, template_name='common_bases/dashboard/generic_delete.html')

    def perform_destroy(self, instance):
        instance.delete()
