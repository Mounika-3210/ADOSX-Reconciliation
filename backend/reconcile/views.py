import csv, io, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Location, SystemARecord, SystemBEntry
from .logic import compare_data


def cors(response):
    response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


def records(model):
    return [row.raw_data for row in model.objects.all()]


def orgs(request):
    if request.method == 'OPTIONS': return cors(JsonResponse({}, status=200))
    org_ids = sorted(set(Location.objects.values_list('org_id', flat=True)))
    return cors(JsonResponse({'orgs': org_ids}))



def discrepancies(request):
    if request.method == 'OPTIONS': return cors(JsonResponse({}, status=200))
    org_id = request.GET.get('org')
    if not org_id:
        return cors(JsonResponse({'error': 'Select an org (tenant) to view its records.'}, status=400))
    rows = compare_data(records(SystemARecord), records(SystemBEntry), list(Location.objects.values()), org_id=org_id)
    reason = request.GET.get('reason', '').strip()
    if reason:
        rows = [r for r in rows if r['reason'] == reason]
    sort = request.GET.get('sort', 'record_id')
    if sort not in {'record_id', 'system_a_value', 'system_b_value', 'reason', 'location_name'}:
        sort = 'record_id'
    rows.sort(key=lambda r: (r.get(sort) or '').lower())
    return cors(JsonResponse({'org': org_id, 'count': len(rows), 'reasons': sorted(set(r['reason'] for r in rows)), 'results': rows}))


@csrf_exempt
def import_csv(request):
    if request.method == 'OPTIONS': return cors(JsonResponse({}, status=200))
    if request.method != 'POST':
        return cors(JsonResponse({'error': 'POST multipart files: system_a, system_b, locations'}, status=405))
    required = ['system_a', 'system_b', 'locations']
    missing = [name for name in required if name not in request.FILES]
    if missing:
        return cors(JsonResponse({'error': 'Missing upload(s): ' + ', '.join(missing)}, status=400))
    try:
        def read_file(upload):
            text = upload.read().decode('utf-8-sig')
            return list(csv.DictReader(io.StringIO(text)))
        a_rows = read_file(request.FILES['system_a'])
        b_rows = read_file(request.FILES['system_b'])
        loc_rows = read_file(request.FILES['locations'])
        # Keep each source row. Missing identifiers get a stable row-based fallback.
        Location.objects.all().delete(); SystemARecord.objects.all().delete(); SystemBEntry.objects.all().delete()
        for i, row in enumerate(loc_rows, 1):
            loc_id = str(row.get('location_id') or f'UNKNOWN-LOCATION-{i}').strip()
            Location.objects.create(location_id=loc_id, org_id=str(row.get('org_id') or 'UNKNOWN-ORG').strip(), location_name=str(row.get('location_name') or '').strip())
        for i, row in enumerate(a_rows, 1):
            rid = str(row.get('record_id') or f'UNIDENTIFIED-A-{i}').strip()
            SystemARecord.objects.create(record_id=rid, location_id=str(row.get('location_id') or '').strip(), raw_data=row)
        for i, row in enumerate(b_rows, 1):
            eid = str(row.get('entry_id') or f'UNIDENTIFIED-B-{i}').strip()
            # protect against duplicate entry_id values while retaining every row
            if SystemBEntry.objects.filter(entry_id=eid).exists(): eid = f'{eid}__ROW{i}'
            SystemBEntry.objects.create(entry_id=eid, record_ref=str(row.get('record_ref') or '').strip(), location_id=str(row.get('location_id') or '').strip(), raw_data=row)
        return cors(JsonResponse({'success': True, 'imported': {'system_a': len(a_rows), 'system_b': len(b_rows), 'locations': len(loc_rows)}}))
    except Exception as exc:
        return cors(JsonResponse({'error': str(exc)}, status=400))
