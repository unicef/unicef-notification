from django.core.exceptions import ValidationError

import pytest

from unicef_notification import validations
from unicef_notification.models import Notification

pytestmark = pytest.mark.django_db


def test_validate_template_name(email_template):
    assert validations.validate_template_name(email_template.name) is None

    with pytest.raises(ValidationError):
        validations.validate_template_name("wrong")


def test_validate_method_type():
    assert validations.validate_method_type(Notification.TYPE_EMAIL) is None

    with pytest.raises(ValidationError):
        validations.validate_method_type("wrong")
