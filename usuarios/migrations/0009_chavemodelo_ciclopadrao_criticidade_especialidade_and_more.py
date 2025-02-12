# Generated by Django 5.1.4 on 2025-02-12 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_alter_customuser_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChaveModelo',
            fields=[
                ('cod_chave', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descricao', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CicloPadrao',
            fields=[
                ('cod_ciclo', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descricao', models.CharField(max_length=255)),
                ('intervalo_dias', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Criticidade',
            fields=[
                ('cod_criticidade', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descricao', models.CharField(max_length=255)),
                ('nivel', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Especialidade',
            fields=[
                ('cod_especialidade', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descricao', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(help_text='E-mail obrigatório para cadastro', max_length=220, unique=True),
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('cod_categoria', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descricao', models.CharField(blank=True, max_length=255, null=True)),
                ('cod_categoria_pai', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias', to='usuarios.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='CategoriaLang',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_idioma', models.CharField(max_length=2)),
                ('descricao', models.CharField(max_length=255)),
                ('cod_categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='traducoes', to='usuarios.categoria')),
            ],
            options={
                'unique_together': {('cod_categoria', 'cod_idioma')},
            },
        ),
        migrations.CreateModel(
            name='MatrizPadraoAtividade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.categoria')),
                ('cod_especialidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.especialidade')),
            ],
            options={
                'unique_together': {('cod_categoria', 'cod_especialidade')},
            },
        ),
    ]
