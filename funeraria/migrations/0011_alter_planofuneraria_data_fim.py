# Generated by Django 5.2.4 on 2025-07-29 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funeraria', '0010_funerariatipos_duracao_em_dias_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planofuneraria',
            name='data_fim',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Fim'),
        ),
    ]
