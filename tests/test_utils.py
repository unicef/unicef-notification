import json
from unittest.mock import patch

import pytest
from django.core.serializers.json import DjangoJSONEncoder

from unicef_notification import utils

pytestmark = pytest.mark.django_db


def test_simple_instance(superuser, group, permission):
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
