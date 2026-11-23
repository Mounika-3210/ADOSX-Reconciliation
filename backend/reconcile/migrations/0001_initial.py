from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='Location', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('location_id', models.CharField(max_length=80, unique=True)), ('org_id', models.CharField(db_index=True, max_length=80)), ('location_name', models.CharField(blank=True, max_length=160))]),
        migrations.CreateModel(name='SystemARecord', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('record_id', models.CharField(db_index=True, max_length=100, unique=True)), ('location_id', models.CharField(blank=True, db_index=True, max_length=80)), ('raw_data', models.JSONField(default=dict))]),
        migrations.CreateModel(name='SystemBEntry', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('entry_id', models.CharField(max_length=120, unique=True)), ('record_ref', models.CharField(blank=True, db_index=True, max_length=100)), ('location_id', models.CharField(blank=True, db_index=True, max_length=80)), ('raw_data', models.JSONField(default=dict))]),
    ]
