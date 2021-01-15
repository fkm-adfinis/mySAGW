import importlib
import inspect

import pytest
from django.core.cache import cache
from factory.base import FactoryMetaClass
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .oidc_auth.models import OIDCUser


def register_module(module):
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, FactoryMetaClass) and not obj._meta.abstract:
            # name needs to be compatible with
            # `rest_framework.routers.SimpleRouter` naming for easier testing
            base_name = obj._meta.model._meta.object_name.lower()
            register(obj, base_name)


register_module(importlib.import_module(".identity.factories", "mysagw"))


@pytest.fixture
def admin_user(settings):
    return OIDCUser(
        "sometoken", {"sub": "admin", settings.OIDC_GROUPS_CLAIM: ["admin"]}
    )


@pytest.fixture
def staff_user(settings):
    return OIDCUser(
        "sometoken",
        {"sub": "staff_user", settings.OIDC_GROUPS_CLAIM: [settings.STAFF_GROUP]},
    )


@pytest.fixture
def user(settings):
    return OIDCUser("sometoken", {"sub": "user", settings.OIDC_GROUPS_CLAIM: []})


@pytest.fixture
def client(db, user, staff_user, admin_user, request):
    user_arg = getattr(request, "param", "admin")
    usermap = {"user": user, "staff": staff_user, "admin": admin_user}

    client = APIClient()
    user = usermap[user_arg]
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture(scope="function", autouse=True)
def _autoclear_cache():
    cache.clear()
