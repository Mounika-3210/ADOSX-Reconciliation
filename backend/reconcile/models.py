from django.db import models

class Location(models.Model):
    location_id = models.CharField(max_length=80, unique=True)
    org_id = models.CharField(max_length=80, db_index=True)
    location_name = models.CharField(max_length=160, blank=True)

class SystemARecord(models.Model):
    record_id = models.CharField(max_length=100, unique=True, db_index=True)
    location_id = models.CharField(max_length=80, blank=True, db_index=True)
    raw_data = models.JSONField(default=dict)

class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=120, unique=True)
    record_ref = models.CharField(max_length=100, blank=True, db_index=True)
    location_id = models.CharField(max_length=80, blank=True, db_index=True)
    raw_data = models.JSONField(default=dict)
