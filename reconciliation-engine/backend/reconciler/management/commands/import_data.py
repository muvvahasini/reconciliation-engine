import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reconciler.models import Location, SystemARecord, SystemBEntry
from reconciler.services.comparator import normalize_reference


class Command(BaseCommand):
    help = 'Import the assessment CSV exports without dropping dirty rows.'

    def add_arguments(self, parser):
        parser.add_argument('--data-dir', default=None, help='Directory containing the three CSV files.')

    @transaction.atomic
    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[4]
        backend_root = Path(__file__).resolve().parents[3]
        base = Path(options['data_dir']) if options['data_dir'] else project_root / 'data'
        if not base.exists():
            base = backend_root / 'data'

        paths = {name: base / name for name in ('locations.csv', 'system_a.csv', 'system_b.csv')}
        missing = [str(p) for p in paths.values() if not p.exists()]
        if missing:
            raise CommandError('Missing CSV files: ' + ', '.join(missing))

        Location.objects.all().delete()
        SystemARecord.objects.all().delete()
        SystemBEntry.objects.all().delete()

        location_count = self._import_locations(paths['locations.csv'])
        a_count = self._import_a(paths['system_a.csv'])
        b_count = self._import_b(paths['system_b.csv'])

        self.stdout.write(self.style.SUCCESS(
            f'Imported {location_count} locations, {a_count} System A rows, {b_count} System B rows.'
        ))
        self.stdout.write('Raw values are preserved; normalization is used only for reconciliation.')

    @staticmethod
    def _reader(path):
        with path.open('r', encoding='utf-8-sig', newline='') as f:
            yield from csv.DictReader(f)

    def _import_locations(self, path):
        rows = list(self._reader(path))
        Location.objects.bulk_create([
            Location(
                location_id=(r.get('location_id') or '').strip(),
                org_id=(r.get('org_id') or '').strip(),
                location_name=(r.get('location_name') or '').strip(),
            ) for r in rows
        ])
        return len(rows)

    def _import_a(self, path):
        objects = []
        for row_number, r in enumerate(self._reader(path), start=2):
            objects.append(SystemARecord(
                record_id=(r.get('record_id') or '').strip(),
                location_id=(r.get('location_id') or '').strip(),
                event_date=(r.get('event_date') or '').strip(),
                category_code=(r.get('category_code') or '').strip(),
                actor_id=(r.get('actor_id') or '').strip(),
                base_value_raw=(r.get('base_value') or '').strip(),
                adjustment_raw=(r.get('adjustment') or '').strip(),
                total_value_raw=(r.get('total_value') or '').strip(),
                state=(r.get('state') or '').strip(),
                source_row_number=row_number,
            ))
        SystemARecord.objects.bulk_create(objects)
        return len(objects)

    def _import_b(self, path):
        objects = []
        for row_number, r in enumerate(self._reader(path), start=2):
            raw_ref = r.get('record_ref') or ''
            objects.append(SystemBEntry(
                entry_id=(r.get('entry_id') or '').strip(),
                record_ref_raw=raw_ref,
                normalized_record_ref=normalize_reference(raw_ref),
                location_id=(r.get('location_id') or '').strip(),
                recorded_on_raw=(r.get('recorded_on') or '').strip(),
                value_raw=(r.get('value') or '').strip(),
                label=(r.get('label') or '').strip(),
                source_row_number=row_number,
            ))
        SystemBEntry.objects.bulk_create(objects)
        return len(objects)
