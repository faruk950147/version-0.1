# Generated by Django 4.2.15 on 2025-03-18 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0002_product_variant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='variant',
            field=models.CharField(choices=[('True', 'True'), ('False', 'False')], default='False', max_length=10),
        ),
    ]
