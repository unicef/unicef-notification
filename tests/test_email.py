from unittest.mock import patch

import pytest
from django.conf import settings
from post_office.models import Email
from tests.factories import NotificationFactory, UserFactory

from unicef_notification.models import Notification

pytestmark = pytest.mark.django_db


def test_email_notification():
    email_qs = Email.objects
    old_email_count = email_qs.count()
    valid_notification = NotificationFactory()
    valid_notification.send_notification()

    assert valid_notification.recipients == valid_notification.sent_recipients
    assert email_qs.count() == old_email_count + 1


class TestSendNotification:
    """
    Test General Notification sending. We currently only have email set up, so
    this only tests that if a non-email type is created, it's an error
    to try to send it.
    """

    def test_send_not_email():
        """
        This just tests that if we currently send a non Email notification,
        sent_recipients doesn't get updated.
        """
        notification = NotificationFactory(type='SMS')
        with pytest.raises(ValueError):
            notification.send_notification()
        assert notification.sent_recipients == []


@patch('unicef_notification.models.mail')
def test_success(mock_mail):
    "On successful notification, sent_recipients should be populated."
    cc = ['joe@example.com']
    notification = NotificationFactory(
        template_data={'foo': 'bar'},
        cc=cc
    )
    mock_mail.send.return_value = Email()
    with patch.object(Notification, 'save'):
        notification.send_mail()
    # we called send with all the proper args
    mock_mail.send.assert_called_with(
        recipients=notification.recipients,
        cc=cc,
        sender=settings.DEFAULT_FROM_EMAIL,
        template=notification.template_name,
        context=notification.template_data,
        html_message='',
        message='',
        subject='',
    )
    # we marked the recipients as sent
    assert notification.recipients + cc == notification.sent_recipients


@patch('unicef_notification.models.mail')
def test_sender_is_user(mock_mail):
    "If sender is a User, send from their email address"
    sender = UserFactory()
    notification = NotificationFactory(sender=sender)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, 'save'):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper email
    assert sender.email == call_kwargs['sender']


@patch('unicef_notification.models.mail')
def test_sender_is_not_a_user(mock_mail):
    "If sender is not a User, send DEFAULT_FROM_EMAIL"
    mock_mail.send.return_value = Email()
    notification = NotificationFactory()
    with patch.object(Notification, 'save'):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper email
    assert settings.DEFAULT_FROM_EMAIL == call_kwargs['sender']


@patch('unicef_notification.models.mail')
def test_template_data_is_dict(mock_mail):
    "We accept a dictionary for the template context."
    template_data = {'foo': 'bar'}
    notification = NotificationFactory(template_data=template_data)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, 'save'):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper context
    assert {'foo': 'bar'} == call_kwargs['context']


@patch('unicef_notification.models.mail')
def test_template_data_is_str(mock_mail):
    "We accept string data for the template context."
    template_data = '{"foo": "bar"}'
    notification = NotificationFactory(template_data=template_data)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, 'save'):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper context
    assert {'foo': 'bar'} == call_kwargs['context']


@patch('unicef_notification.models.mail')
def test_ignore_mail_sending_error(mock_mail):
    "If sending throws an error, we log and continue."
    mock_mail.send.side_effect = Exception()
    notification = NotificationFactory()
    mock_mail.send.return_value = Email()
    with patch.object(Notification, 'save'):
        with patch('unicef_notification.models.logger') as mock_logger:
            notification.send_mail()
    mock_logger.exception.assert_called_with('Failed to send mail.')
    # recipients weren't marked as successful
    assert notification.sent_recipients == []
