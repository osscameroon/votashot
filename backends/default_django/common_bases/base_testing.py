"""This module contains the classes helpers to help in various testing"""
from rest_framework.reverse import reverse

from .base_factories import get_data_from_baker
from model_bakery import baker
from django.contrib.auth import get_user_model
from uni_ps.utils import add_permission_to_user

User = get_user_model()


class GenericViewSetTestCaseMixin:
    """This base class help in testing a generic (models) viewset."""

    viewset_basename = ""
    api_namespace = "api"
    model = None
    allowed_actions = [
        "create",
        "retrieve",
        "update",
        "partial_update",
        "destroy",
    ]
    primary_key = "id"
    single_lookup_key = "pk"
    serializer_class = None

    def _authenticate_client(self):
        if not getattr(self, 'user', None):
            self.user = baker.make(User, is_active=True)
        self.client.force_authenticate(self.user)

    @property
    def viewset_base_endpoint(self):
        if self.api_namespace:
            return f"{self.api_namespace}:{self.viewset_basename}"
        else:
            return self.viewset_basename
        
    def get_serializer(self):
        return self.serializer_class() if self.serializer_class else None

    def test_create_fail(self):
        """This test sends empty dictionary to the create endpoint and make checks
        that the api returns 400 Bad Request"""
        self._authenticate_client()
        url = reverse(f"{self.viewset_base_endpoint}-list")
        data = {}
        response = self.client.post(url, data=data, format="json")
        self.print_if_status_code_not(response, 400)
        self.assertEqual(response.status_code, 400)
        return data, response

    def fields_overrides_for_create(self):
        return None

    def fields_overrides_for_update(self):
        return None

    def test_create_success(self):
        self._authenticate_client()
        url = reverse(f"{self.viewset_base_endpoint}-list")
        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_create())
        response = self.client.post(url, data=data, format="json")
        self.print_if_status_code_not(response, 201)
        self.assertEqual(response.status_code, 201)
        return data, response

    def test_retrieve_success(self):
        self._authenticate_client()
        url = reverse(f"{self.viewset_base_endpoint}-list")
        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_create())
        response = self.client.post(url, data=data, format="json")
        self.print_if_status_code_not(response, 201)
        self.assertEqual(response.status_code, 201)
        old_data = response.data
        pk = old_data.get(self.primary_key)

        add_permission_to_user(self.user, self.model(**{'pk': pk, self.primary_key: pk}))

        url = reverse(
            f"{self.viewset_base_endpoint}-detail",
            kwargs={self.single_lookup_key: pk},
        )
        response = self.client.get(url, format="json")
        self.print_if_status_code_not(response, 200)
        self.assertEqual(response.status_code, 200)
        return data, response

    def test_update_success(self):
        self._authenticate_client()
        url = reverse(f"{self.viewset_base_endpoint}-list")
        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_create())
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.print_if_status_code_not(response, 201)
        old_data = response.data

        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_update())
        pk = old_data.get(self.primary_key)

        add_permission_to_user(self.user, self.model(**{'pk': pk, self.primary_key: pk}))

        url = reverse(
            f"{self.viewset_base_endpoint}-detail",
            kwargs={self.single_lookup_key: pk},
        )
        response = self.client.put(url, data=data, format="json")
        self.print_if_status_code_not(response, 200)
        self.assertEqual(response.status_code, 200)
        return data, response

    def test_partial_update_success(self):
        self._authenticate_client()
        url = reverse(f"{self.viewset_base_endpoint}-list")
        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_create())
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.print_if_status_code_not(response, 201)
        old_data = response.data

        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_update())
        pk = old_data.get(self.primary_key)

        add_permission_to_user(self.user, self.model(**{'pk': pk, self.primary_key: pk}))

        url = reverse(
            f"{self.viewset_base_endpoint}-detail",
            kwargs={self.single_lookup_key: pk},
        )
        response = self.client.patch(url, data=data, format="json")
        self.print_if_status_code_not(response, 200)
        self.assertEqual(response.status_code, 200)
        return data, response

    def test_destroy_success(self):
        self._authenticate_client()
        url = reverse(f"{self.viewset_base_endpoint}-list")
        data = get_data_from_baker(self.model, serializer=self.get_serializer(),
                                   _fields_overrides=self.fields_overrides_for_create(),
                                   )
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.print_if_status_code_not(response, 201)
        old_data = response.data

        data = get_data_from_baker(self.model)
        pk = old_data.get(self.primary_key)

        add_permission_to_user(self.user, self.model(**{'pk': pk, self.primary_key: pk}))

        self.user.refresh_from_db()

        url = reverse(
            f"{self.viewset_base_endpoint}-detail",
            kwargs={self.single_lookup_key: pk},
        )
        response = self.client.delete(url, data=data, format="json")
        self.print_if_status_code_not(response, 204)
        self.assertEqual(response.status_code, 204)
        return data, response

    def print_if_status_code_not(self, response, status_code):
        if response.status_code != status_code:
            print(response.data)
