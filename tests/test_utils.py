import json
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from post_office.models import Email

from unicef_notification import utils
from unicef_notification.models import Notification

pytestmark = pytest.mark.django_db


def test_model_to_dictionary(superuser, group, permission):
    superuser.groups.add(group)
    superuser.user_permissions.add(permission)
    result = utils.model_to_dictionary(superuser)

    date_joined_serialized = json.loads(
        json.dumps(superuser.date_joined, cls=DjangoJSONEncoder)
    )

    assert result == {
        'username': superuser.username,
        'first_name': '',
        'last_name': '',
        'is_active': True,
        'is_superuser': True,
        'is_staff': False,
        'last_login': None,
        'groups': [group.pk],
        'user_permissions': [permission.pk],
        'pk': superuser.pk,
        'model': 'auth.user',
        'password': '',
        'email': superuser.email,
        'date_joined': date_joined_serialized,
    }


def test_serialize_dict(user):
    with patch('unicef_notification.utils.model_to_dictionary') as mock_serialize:
        mock_serialize.return_value = {'exclamation': 'Hello, world!'}
        d = {
            'i': 27,
            's': 'Foo',
            'user': user,
        }
        result = utils.serialize_dict(d)
        assert result == {
            'i': 27,
            's': 'Foo',
            'user': {
                'exclamation': 'Hello, world!'
            }
        }


def test_strip_text():
    assert utils.strip_text("   hello \n  world") == "hello \r\nworld"


def test_get_template_content():
    assert utils.get_template_content("content", None) == "content"


def test_get_template_content_filename(file_html):
    assert utils.get_template_content(None, file_html) == "Hello World!\n"


def test_get_template_content_neither():
    assert utils.get_template_content(None, None) == ""


@patch('unicef_notification.models.mail')
def test_send_notification(mock_mail, file_html):
    mock_mail.send.return_value = Email()
    recipients = ["test@example.com"]
    with patch.object(Notification, 'save'):
        utils.send_notification(
            recipients,
            content_filename=file_html
        )
    # we called send with all the proper args
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    assert settings.DEFAULT_FROM_EMAIL == call_kwargs['sender']
    assert recipients == call_kwargs["recipients"]


@patch('unicef_notification.models.mail')
def test_send_notification_from_address(mock_mail, file_html):
    mock_mail.send.return_value = Email()
    recipients = ["test@example.com"]
    from_address = "from@example.com"
    with patch.object(Notification, 'save'):
        utils.send_notification(
            recipients,
            from_address=from_address,
            content_filename=file_html
        )
    # we called send with all the proper args
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    assert from_address == call_kwargs['sender']
    assert recipients == call_kwargs["recipients"]


@patch('unicef_notification.models.mail')
def test_send_notification_with_template(mock_mail, email_template):
    mock_mail.send.return_value = Email()
    recipients = ["test@example.com"]
    with patch.object(Notification, 'save'):
        utils.send_notification_with_template(
            recipients,
            email_template.name,
            {}
        )
    # we called send with all the proper args
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    assert settings.DEFAULT_FROM_EMAIL == call_kwargs['sender']
    assert recipients == call_kwargs["recipients"]


@patch('unicef_notification.models.mail')
def test_send_notification_with_template_from_address(mock_mail, email_template):
    mock_mail.send.return_value = Email()
    recipients = ["test@example.com"]
    from_address = "from@example.com"
    with patch.object(Notification, 'save'):
        utils.send_notification_with_template(
            recipients,
            email_template.name,
            {},
            from_address=from_address,
        )
    # we called send with all the proper args
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    assert from_address == call_kwargs['sender']
    assert recipients == call_kwargs["recipients"]
