import json

import factory
from demo.sample.models import Author
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from unicef_notification import models


# Credit goes to http://stackoverflow.com/a/41154232/2363915
class JSONFieldFactory(factory.DictFactory):

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        if args:
            raise ValueError(
                "DictFactory %r does not support Meta.inline_args.", cls)
        return json.dumps(model_class(**kwargs))


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = get_user_model()


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = Group


class AuthorFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = Author


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Notification

    type = "Email"
    sender = factory.SubFactory(AuthorFactory)
    template_name = 'trips/trip/TA_request'
    recipients = ['test@example.com', 'test1@example.com', 'test2@example.com']
    template_data = factory.Dict(
        {
            'url': 'www.unicef.org',
            'pa_assistant': 'Test revised',
            'owner_name': 'Tester revised'
        },
        dict_factory=JSONFieldFactory
    )
