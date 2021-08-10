import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from model_utils import Choices
from post_office import mail
from post_office.models import EmailTemplate  # noqa used as a wrapper

from unicef_notification import validations
from unicef_notification.utils import serialize_dict

logger = logging.getLogger(__name__)


class Notification(models.Model):
    """
    Represents a notification instance from sender to recipients
    """

    TYPE_EMAIL = "Email"
    TYPE_CHOICES = Choices(
        (TYPE_EMAIL, 'Email'),
    )

    method_type = models.CharField(
        verbose_name=_('Type'),
        max_length=255,
        default=TYPE_EMAIL,
        validators=[validations.validate_method_type],
    )
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('Content Type'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('Object ID'),
        null=True,
        blank=True,
    )
    sender = GenericForeignKey('content_type', 'object_id')
    # from_address can be used as the notification from address if sender is
    # not a user with an email address.
    from_address = models.CharField(max_length=255, null=True, blank=True)
    recipients = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        verbose_name=_('Recipients')
    )
    cc = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
    )
    sent_recipients = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        verbose_name=_('Sent Recipients')
    )
    # template_name has to be the name of an existing EmailTemplate object.
    # validate_template_name checks that.
    template_name = models.CharField(
        verbose_name=_('Template Name'),
        max_length=255,
        validators=[validations.validate_template_name],
        blank=True,
        default='',
    )
    # template_data is the context for rendering any templates.
    template_data = models.JSONField(
        verbose_name=_('Template Data'),
        null=True,
        blank=True,
    )
    # Save a link to the actual post_office.Email object that was sent
    sent_email = models.ForeignKey(
        'post_office.Email',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # Content of template used to render subject
    # if template_name not specified.
    subject = models.TextField(default='', blank=True)
    # Content of template used to render plain text message
    # if template_name not specified.
    text_message = models.TextField(default='', blank=True)
    # Content of template used to render HTML message
    # if template_name not specified.
    html_message = models.TextField(default='', blank=True)

    def __str__(self):
        return "{} Notification from {}: {}".format(
            self.method_type,
            self.sender,
            self.template_data
        )

    def __init__(self, *args, **kwargs):
        template_data = kwargs.pop('template_data', {})
        # Before trying to serialize template_data, we might need to
        # make it serializable
        try:
            json.dumps(template_data)
        except TypeError:
            assert isinstance(template_data, dict)
            template_data = serialize_dict(template_data)
        kwargs['template_data'] = template_data
        super(Notification, self).__init__(*args, **kwargs)

    def clean(self):
        if (self.text_message or self.html_message or self.subject) and self.template_name:
            raise ValidationError(
                "Notification cannot have both a template name, "
                "and a text_message or html_message or subject"
            )
        if not (self.text_message or self.html_message or self.template_name or self.subject):
            raise ValidationError(
                "Notification must have template name or text_message or html_message or subject."
            )
        # We won't require there to be any recipients, since callers might find
        # it easier to just call this with whatever list of email addresses
        # they have without having to first check whether they have any
        # addresses.
        # if not (len(self.cc) + len(self.recipients)):
        #     raise ValidationError("Notification must have at least one recipient or cc address.")

    def send_notification(self):
        """
        Dispatch notification based on type.
        """
        if self.method_type == self.TYPE_EMAIL:
            self.send_mail()
        else:
            # for future notification methods
            raise ValueError("Unknown notification type: %s" % self.method_type)

    def send_mail(self):
        User = get_user_model()

        if isinstance(self.sender, User):
            sender = self.sender.email
        elif self.from_address:
            sender = self.from_address
        else:
            sender = settings.DEFAULT_FROM_EMAIL

        if isinstance(self.template_data, str):
            template_data = json.loads(self.template_data)
        else:
            template_data = self.template_data

        try:
            email = mail.send(
                recipients=self.recipients,
                cc=self.cc,
                sender=sender,
                template=self.template_name,
                context=template_data,
                subject=self.subject,  # actually template text
                message=self.text_message,  # actually template text
                html_message=self.html_message,  # actually template text
            )
        except Exception:
            # log an exception, with traceback
            logger.exception('Failed to send mail.')
        else:
            self.sent_recipients = self.recipients + self.cc
            self.sent_email = email
            self.save()
