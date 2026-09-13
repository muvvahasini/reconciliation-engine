from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_id', models.CharField(max_length=64, unique=True)),
                ('org_id', models.CharField(db_index=True, max_length=64)),
                ('location_name', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SystemARecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_id', models.CharField(max_length=128, unique=True)),
                ('location_id', models.CharField(db_index=True, max_length=64)),
                ('event_date', models.CharField(blank=True, max_length=64)),
                ('category_code', models.CharField(blank=True, max_length=64)),
                ('actor_id', models.CharField(blank=True, max_length=128)),
                ('base_value_raw', models.TextField(blank=True)),
                ('adjustment_raw', models.TextField(blank=True)),
                ('total_value_raw', models.TextField(blank=True)),
                ('state', models.CharField(blank=True, max_length=128)),
                ('source_row_number', models.PositiveIntegerField()),
            ],
            options={'ordering': ['record_id']},
        ),
        migrations.CreateModel(
            name='SystemBEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_id', models.CharField(max_length=128, unique=True)),
                ('record_ref_raw', models.TextField(blank=True)),
                ('normalized_record_ref', models.CharField(blank=True, db_index=True, max_length=128)),
                ('location_id', models.CharField(db_index=True, max_length=64)),
                ('recorded_on_raw', models.TextField(blank=True)),
                ('value_raw', models.TextField(blank=True)),
                ('label', models.TextField(blank=True)),
                ('source_row_number', models.PositiveIntegerField()),
            ],
            options={'ordering': ['entry_id']},
        ),
    ]
