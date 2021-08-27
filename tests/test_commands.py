from django.core.management import call_command

from post_office.models import EmailTemplate

import pytest

pytestmark = pytest.mark.django_db


def test_update_notifications():
    email_qs = EmailTemplate.objects
    init_count = email_qs.count()
    call_command("update_notifications")
    assert email_qs.count() == init_count + 1
