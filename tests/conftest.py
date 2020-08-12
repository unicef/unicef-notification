from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission

import pytest

from tests import factories


@pytest.fixture()
def base_email_template():
    return factories.EmailTemplateFactory(
        name="test_base",
        html_content='''
        <html>
            <head></head>
            <body>
                <h1>Base template</h1>
                {% block content %}{% endblock %}
            </body>
        </html>
        '''
    )


@pytest.fixture()
def email_template(base_email_template):
    return factories.EmailTemplateFactory(
        name='template1',
        html_content='''
        {% extends "email-templates/test_base" %}

        {% block content %}
            <p>Template1</p>
        {% endblock %}
        '''
    )


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


@pytest.fixture
def notification(email_template):
    return factories.NotificationFactory(template_name=email_template.name)


@pytest.fixture
def file_html():
    return "test.html"
