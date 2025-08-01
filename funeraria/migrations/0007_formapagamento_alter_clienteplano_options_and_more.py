# Generated by Django 5.2.4 on 2025-07-28 23:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funeraria', '0006_alter_funerariatipos_options_funerariatipos_valor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormaPagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=100, verbose_name='Descrição')),
                ('categoria', models.CharField(default='pagamento', help_text='Categoria da forma de pagamento', max_length=20, verbose_name='Categoria')),
            ],
            options={
                'verbose_name': 'Forma de Pagamento',
                'verbose_name_plural': 'Formas de Pagamento',
                'db_table': 'forma_pagamento',
            },
        ),
        migrations.AlterModelOptions(
            name='clienteplano',
            options={'verbose_name': 'Cliente Plano', 'verbose_name_plural': 'Clientes Planos'},
        ),
        migrations.AlterUniqueTogether(
            name='clienteplano',
            unique_together={('cliente', 'plano')},
        ),
        migrations.AddField(
            model_name='funerariastatus',
            name='categoria',
            field=models.CharField(choices=[('cliente', 'Cliente'), ('pagamento', 'Pagamento')], default='2025-12-31', help_text='Categoria a qual o status pertence: cliente ou pagamento', max_length=20, verbose_name='Categoria'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clientefuneraria',
            name='cliente_status',
            field=models.ForeignKey(limit_choices_to={'categoria': 'cliente'}, on_delete=django.db.models.deletion.PROTECT, to='funeraria.funerariastatus', verbose_name='Status do Cliente'),
        ),
        migrations.AlterField(
            model_name='clienteplano',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planos_cliente', to='funeraria.clientefuneraria', verbose_name='Cliente'),
        ),
        migrations.AlterField(
            model_name='clienteplano',
            name='data_fim',
            field=models.DateField(verbose_name='Data de Fim'),
        ),
        migrations.AlterField(
            model_name='clienteplano',
            name='plano',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clientes_plano', to='funeraria.planofuneraria', verbose_name='Plano'),
        ),
        migrations.AlterField(
            model_name='funerariatipos',
            name='categoria',
            field=models.CharField(choices=[('plano', 'Plano'), ('servico', 'Serviço'), ('renovacao', 'Renovação')], default='plano', max_length=50, verbose_name='Categoria do Tipo'),
        ),
        migrations.AlterField(
            model_name='pagamentofuneraria',
            name='status_pagamento',
            field=models.ForeignKey(limit_choices_to={'categoria': 'pagamento'}, on_delete=django.db.models.deletion.PROTECT, to='funeraria.funerariastatus', verbose_name='Status do Pagamento'),
        ),
        migrations.AlterField(
            model_name='planofuneraria',
            name='tipo_plano',
            field=models.ForeignKey(limit_choices_to={'categoria': 'plano'}, on_delete=django.db.models.deletion.PROTECT, related_name='planos_funerarios', to='funeraria.funerariatipos', verbose_name='Tipo do Plano'),
        ),
        migrations.AlterField(
            model_name='planofuneraria',
            name='tipo_renovacao',
            field=models.ForeignKey(blank=True, limit_choices_to={'categoria': 'renovacao'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='planos_com_renovacao', to='funeraria.funerariatipos', verbose_name='Tipo de Renovação'),
        ),
        migrations.AlterField(
            model_name='pagamentofuneraria',
            name='forma_pagamento',
            field=models.ForeignKey(limit_choices_to={'categoria': 'pagamento'}, on_delete=django.db.models.deletion.PROTECT, to='funeraria.formapagamento', verbose_name='Forma de Pagamento'),
        ),
        migrations.RemoveField(
            model_name='clienteplano',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='clienteplano',
            name='funcionario_atualizacao',
        ),
        migrations.RemoveField(
            model_name='clienteplano',
            name='funcionario_cadastro',
        ),
        migrations.RemoveField(
            model_name='clienteplano',
            name='updated_at',
        ),
        migrations.CreateModel(
            name='ClienteDependentePlano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio', models.DateField(verbose_name='Data de Início')),
                ('data_fim', models.DateField(verbose_name='Data de Fim')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('dependente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planos_dependente', to='funeraria.dependentefuneraria', verbose_name='Dependente')),
                ('plano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dependentes_plano', to='funeraria.planofuneraria', verbose_name='Plano')),
            ],
            options={
                'verbose_name': 'Dependente Plano',
                'verbose_name_plural': 'Dependentes Planos',
                'db_table': 'cliente_dependente_plano',
                'unique_together': {('dependente', 'plano')},
            },
        ),
    ]
