from django.template import TemplateDoesNotExist
from post_office.models import Email

import pytest
from unittest.mock import Mock

from unicef_notification import loaders
from unicef_notification.utils import send_notification_with_template

pytestmark = pytest.mark.django_db


def test_extends(email_template):
    mail_qs = Email.objects
    assert mail_qs.count() == 0
    send_notification_with_template(
        recipients=['test@example.com'],
        from_address='no-reply@test.com',
        template_name='template1',
        context={},
    )

    assert mail_qs.count() == 1
    mail = mail_qs.first()
    assert 'Base template' in mail.html_message
    assert 'Template1' in mail.html_message


def test_get_template_sources(email_template):
    loader = loaders.EmailTemplateLoader(engine=None)
    template_name = "{}{}".format(
        loaders.EMAIL_TEMPLATE_PREFIX,
        email_template.name
    )
    templates = loader.get_template_sources(template_name=template_name)
    assert len(list(templates)) == 1


def test_get_template_sources_invalid():
    loader = loaders.EmailTemplateLoader(engine=None)
    templates = loader.get_template_sources(template_name="wrong/template")
    assert list(templates) == []


def test_get_contents_invalid():
    loader = loaders.EmailTemplateLoader(engine=None)
    mock_origin = Mock()
    mock_origin.name = "wrong"
    assert loader.get_contents(mock_origin) is None


def test_get_contents(email_template):
    loader = loaders.EmailTemplateLoader(engine=None)
    mock_origin = Mock()
    mock_origin.name = email_template.name
    assert loader.get_contents(mock_origin) == email_template.html_content


def test_load_template_source_invalid():
    """Template does not exist"""
    loader = loaders.EmailTemplateLoader(engine=None)
    with pytest.raises(TemplateDoesNotExist):
        loader.load_template_source(
            "{}wrong".format(loaders.EMAIL_TEMPLATE_PREFIX)
        )


def test_load_template_source_not_found(email_template):
    """Template exists but name does not start with template prefix"""
    loader = loaders.EmailTemplateLoader(engine=None)
    with pytest.raises(TemplateDoesNotExist):
        loader.load_template_source(email_template.name)


def test_load_template_source(email_template):
    loader = loaders.EmailTemplateLoader(engine=None)
    template_name = "{}{}".format(
        loaders.EMAIL_TEMPLATE_PREFIX,
        email_template.name
    )
    content, name = loader.load_template_source(template_name)
    assert content == email_template.html_content
    assert name == email_template.name
