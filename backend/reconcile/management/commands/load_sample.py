import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from reconcile.models import Location, SystemARecord, SystemBEntry

class Command(BaseCommand):
    help = 'Load the assessment CSVs bundled in sample_data into the local database.'
    def handle(self, *args, **options):
        root = Path(__file__).resolve().parents[4] / 'sample_data'
        def read(name):
            with open(root / name, newline='', encoding='utf-8-sig') as f:
                return list(csv.DictReader(f))
        locs, aa, bb = read('locations.csv'), read('system_a.csv'), read('system_b.csv')
        Location.objects.all().delete(); SystemARecord.objects.all().delete(); SystemBEntry.objects.all().delete()
        for row in locs:
            Location.objects.create(location_id=row.get('location_id') or 'UNKNOWN', org_id=row.get('org_id') or 'UNKNOWN', location_name=row.get('location_name') or '')
        for i, row in enumerate(aa, 1):
            rid = row.get('record_id') or f'UNIDENTIFIED-A-{i}'
            SystemARecord.objects.create(record_id=rid, location_id=row.get('location_id') or '', raw_data=row)
        for i, row in enumerate(bb, 1):
            eid = row.get('entry_id') or f'UNIDENTIFIED-B-{i}'
            if SystemBEntry.objects.filter(entry_id=eid).exists(): eid += f'__ROW{i}'
            SystemBEntry.objects.create(entry_id=eid, record_ref=row.get('record_ref') or '', location_id=row.get('location_id') or '', raw_data=row)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(aa)} System A, {len(bb)} System B, {len(locs)} locations.'))
