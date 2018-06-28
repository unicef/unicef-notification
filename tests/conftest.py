import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from tests import factories


@pytest.fixture()
def email_template():
    return factories.EmailTemplateFactory()


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def user():
    return factories.UserFactory()


@pytest.fixture
def superuser():
    return factories.UserFactory(
        username="superusername",
        email="super@example.com",
        is_superuser=True,
    )


@pytest.fixture
def group():
    return factories.GroupFactory()


@pytest.fixture
def permission():
    return Permission.objects.first()


@pytest.fixture
def author():
    return factories.AuthorFactory()
