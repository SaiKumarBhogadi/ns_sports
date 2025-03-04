# Generated by Django 4.2.19 on 2025-02-22 05:08

import blog_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0004_remove_blog_image_blogimage'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', blog_app.models.CustomUserManager()),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='password_reset_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
