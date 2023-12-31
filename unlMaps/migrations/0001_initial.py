# Generated by Django 4.2.2 on 2023-07-13 04:43

from django.db import migrations, models
import django.db.models.deletion
import unlMaps.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Facultad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('sigla', models.CharField(max_length=100)),
                ('decano', models.CharField(max_length=100)),
                ('foto', models.ImageField(upload_to=unlMaps.utils.get_image_path)),
            ],
        ),
        migrations.CreateModel(
            name='Mapa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('grafo', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Punto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=100)),
                ('latitud', models.CharField(max_length=100)),
                ('longitud', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=200)),
                ('facultad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unlMaps.facultad')),
            ],
        ),
        migrations.CreateModel(
            name='Bloque',
            fields=[
                ('punto_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unlMaps.punto')),
                ('informacion', models.CharField(max_length=100)),
                ('valoracion', models.IntegerField(default=0)),
                ('foto', models.ImageField(upload_to=unlMaps.utils.get_image_path)),
            ],
            bases=('unlMaps.punto',),
        ),
        migrations.AddField(
            model_name='facultad',
            name='mapa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unlMaps.mapa'),
        ),
        migrations.CreateModel(
            name='Cuenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('usuario', models.CharField(max_length=100)),
                ('contrasenia', models.CharField(max_length=100)),
                ('mapa', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='unlMaps.mapa')),
            ],
        ),
        migrations.CreateModel(
            name='Conexion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodo_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conexiones_entrantes', to='unlMaps.punto')),
                ('nodo_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conexiones_salientes', to='unlMaps.punto')),
            ],
        ),
    ]
