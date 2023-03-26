# Generated by Django 4.0.2 on 2023-03-24 04:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_likepost_post_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followerscount',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.profile'),
        ),
        migrations.AlterField(
            model_name='followerscount',
            name='user',
            field=models.CharField(max_length=200),
        ),
    ]