from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=64, unique=True)
    org_id = models.CharField(max_length=64, db_index=True)
    location_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.location_id} ({self.org_id})'


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=128, unique=True)
    location_id = models.CharField(max_length=64, db_index=True)
    event_date = models.CharField(max_length=64, blank=True)
    category_code = models.CharField(max_length=64, blank=True)
    actor_id = models.CharField(max_length=128, blank=True)
    base_value_raw = models.TextField(blank=True)
    adjustment_raw = models.TextField(blank=True)
    total_value_raw = models.TextField(blank=True)
    state = models.CharField(max_length=128, blank=True)
    source_row_number = models.PositiveIntegerField()

    class Meta:
        ordering = ['record_id']


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=128, unique=True)
    record_ref_raw = models.TextField(blank=True)
    normalized_record_ref = models.CharField(max_length=128, db_index=True, blank=True)
    location_id = models.CharField(max_length=64, db_index=True)
    recorded_on_raw = models.TextField(blank=True)
    value_raw = models.TextField(blank=True)
    label = models.TextField(blank=True)
    source_row_number = models.PositiveIntegerField()

    class Meta:
        ordering = ['entry_id']
