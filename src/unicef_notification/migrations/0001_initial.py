# Generated by Django 2.0.6 on 2018-06-27 14:48

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models

import unicef_notification.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('post_office', '0006_attachment_mimetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_type', models.CharField(default='Email', max_length=255, validators=[unicef_notification.validations.validate_method_type], verbose_name='Type')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Object ID')),
                ('from_address', models.CharField(blank=True, max_length=255, null=True)),
                ('recipients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, size=None, verbose_name='Recipients')),
                ('cc', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None)),
                ('sent_recipients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None, verbose_name='Sent Recipients')),
                ('template_name', models.CharField(blank=True, default='', max_length=255, validators=[unicef_notification.validations.validate_template_name], verbose_name='Template Name')),
                ('template_data', models.JSONField(blank=True, null=True, verbose_name='Template Data')),
                ('subject', models.TextField(blank=True, default='')),
                ('text_message', models.TextField(blank=True, default='')),
                ('html_message', models.TextField(blank=True, default='')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Content Type')),
                ('sent_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='post_office.Email')),
            ],
        ),
    ]
