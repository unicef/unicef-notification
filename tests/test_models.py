from django.conf import settings
from django.core.exceptions import ValidationError

from post_office.models import Email

import pytest
from unittest.mock import patch

from tests.factories import AuthorFactory, NotificationFactory, UserFactory
from unicef_notification.models import Notification
from unicef_notification.utils import serialize_dict

from demo.sample.models import Author

pytestmark = pytest.mark.django_db


def test_notification_str(notification):
    author = Author(name="xyz")
    notification.sender = author

    assert "Email Notification from" in str(notification)
    assert "from xyz" in str(notification)

    author = AuthorFactory(name="R\xe4dda Barnen")
    notification.sender = author
    assert "Email Notification from" in str(notification)
    assert "from R\xe4dda Barnen" in str(notification)


def test_init_json():
    notification = Notification(template_data={"name": "Test"})
    assert notification.template_data == {"name": "Test"}


def test_init_serialize(author):
    notification = Notification(template_data={"author": author})
    assert notification.template_data == serialize_dict({"author": author})


def test_clean(notification):
    assert notification.clean() is None


def test_clean_clashes(notification):
    notification.text_message = "New"
    with pytest.raises(ValidationError):
        notification.clean()


def test_clean_missing(notification):
    notification.template_name = None
    with pytest.raises(ValidationError):
        notification.clean()


def test_send_notification(notification):
    email_qs = Email.objects
    old_email_count = email_qs.count()
    notification.send_notification()
    assert notification.recipients == notification.sent_recipients
    assert email_qs.count() == old_email_count + 1


def test_send_notification_not_email(notification):
    """This just tests that if we currently send a non Email notification,
    sent_recipients doesn't get updated.
    """
    notification.method_type = "SMS"
    with pytest.raises(ValueError):
        notification.send_notification()
    assert notification.sent_recipients == []


@patch("unicef_notification.models.mail")
def test_success(mock_mail):
    "On successful notification, sent_recipients should be populated."
    cc = ["joe@example.com"]
    notification = NotificationFactory(template_data={"foo": "bar"}, cc=cc)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, "save"):
        notification.send_mail()
    # we called send with all the proper args
    mock_mail.send.assert_called_with(
        recipients=notification.recipients,
        cc=cc,
        sender=settings.DEFAULT_FROM_EMAIL,
        template=notification.template_name,
        context=notification.template_data,
        html_message="",
        message="",
        subject="",
    )
    # we marked the recipients as sent
    assert notification.recipients + cc == notification.sent_recipients


@patch("unicef_notification.models.mail")
def test_sender_is_user(mock_mail):
    "If sender is a User, send from their email address"
    sender = UserFactory()
    notification = NotificationFactory(sender=sender)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, "save"):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper email
    assert sender.email == call_kwargs["sender"]


@patch("unicef_notification.models.mail")
def test_sender_is_not_a_user(mock_mail):
    "If sender is not a User, send DEFAULT_FROM_EMAIL"
    mock_mail.send.return_value = Email()
    notification = NotificationFactory()
    with patch.object(Notification, "save"):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper email
    assert settings.DEFAULT_FROM_EMAIL == call_kwargs["sender"]


@patch("unicef_notification.models.mail")
def test_sender_is_from_address(mock_mail):
    "If sender is not a User, use from address if set"
    mock_mail.send.return_value = Email()
    from_address = "from@example.com"
    notification = NotificationFactory(from_address=from_address)
    with patch.object(Notification, "save"):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper email
    assert from_address == call_kwargs["sender"]


@patch("unicef_notification.models.mail")
def test_template_data_is_dict(mock_mail):
    "We accept a dictionary for the template context."
    template_data = {"foo": "bar"}
    notification = NotificationFactory(template_data=template_data)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, "save"):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper context
    assert {"foo": "bar"} == call_kwargs["context"]


@patch("unicef_notification.models.mail")
def test_template_data_is_str(mock_mail):
    "We accept string data for the template context."
    template_data = '{"foo": "bar"}'
    notification = NotificationFactory(template_data=template_data)
    mock_mail.send.return_value = Email()
    with patch.object(Notification, "save"):
        notification.send_mail()
    # we called send ...
    mock_mail.send.assert_called()
    call_kwargs = mock_mail.send.call_args[1]
    # ... with the proper context
    assert {"foo": "bar"} == call_kwargs["context"]


@patch("unicef_notification.models.mail")
def test_ignore_mail_sending_error(mock_mail):
    "If sending throws an error, we log and continue."
    mock_mail.send.side_effect = Exception()
    notification = NotificationFactory()
    mock_mail.send.return_value = Email()
    with patch.object(Notification, "save"):
        with patch("unicef_notification.models.logger") as mock_logger:
            notification.send_mail()
    mock_logger.exception.assert_called_with("Failed to send mail.")
    # recipients weren't marked as successful
    assert notification.sent_recipients == []
