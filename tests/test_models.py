import pytest
from demo.sample.models import Author
from tests.factories import AuthorFactory, NotificationFactory

pytestmark = pytest.mark.django_db


def test_notification_str():
    author = Author(name='xyz')
    notification = NotificationFactory(sender=author)

    assert 'Email Notification from' in str(notification)
    assert 'from xyz' in str(notification)

    author = AuthorFactory(name='R\xe4dda Barnen')
    notification = NotificationFactory(sender=author)
    assert 'Email Notification from' in str(notification)
    assert 'from R\xe4dda Barnen' in str(notification)
