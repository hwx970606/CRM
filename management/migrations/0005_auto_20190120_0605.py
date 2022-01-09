# Generated by Django 2.1.4 on 2019-01-20 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_auto_20190120_0500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='depart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Depart', verbose_name='部门'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='gender',
            field=models.IntegerField(choices=[(1, '男'), (2, '女')], default=1, verbose_name='性别'),
        ),
    ]