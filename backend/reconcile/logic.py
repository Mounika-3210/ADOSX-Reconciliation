import re
from decimal import Decimal, InvalidOperation


def normalize_ref(value):
    """Normalize references like REC-1112, 1112, or ' rec-1112 ' to REC-1112."""
    value = str(value or '').strip().upper()
    value = re.sub(r'[^A-Z0-9]', '', value)
    if not value:
        return ''
    if value.startswith('REC'):
        suffix = value[3:]
    else:
        suffix = value
    return f'REC-{suffix}' if suffix.isdigit() else f'REC-{suffix}'


def safe_decimal(value):
    try:
        cleaned = str(value or '').strip().replace(',', '')
        if not cleaned:
            return None
        return Decimal(cleaned)
    except (InvalidOperation, ValueError, TypeError):
        return None


def compare_data(system_a, system_b, locations, org_id=None):
    """Return discrepancies limited to a tenant. Inputs are lists of dictionaries."""
    loc_org = {str(x.get('location_id', '')).strip(): str(x.get('org_id', '')).strip() for x in locations}
    loc_name = {str(x.get('location_id', '')).strip(): str(x.get('location_name', '')).strip() for x in locations}
    a_rows = [a for a in system_a if loc_org.get(str(a.get('location_id', '')).strip()) == org_id] if org_id else list(system_a)
    b_rows = [b for b in system_b if loc_org.get(str(b.get('location_id', '')).strip()) == org_id] if org_id else list(system_b)
    a_by_norm = {normalize_ref(a.get('record_id')): a for a in a_rows}
    b_groups = {}
    out = []
    def item(reason, record, a, b, location_id, detail=''):
        out.append({
            'reason': reason, 'record_id': record or '-', 'location_id': location_id or '-',
            'location_name': loc_name.get(location_id, ''),
            'system_a_value': (a or {}).get('total_value', '') if a else '',
            'system_b_value': (b or {}).get('value', '') if b else '',
            'system_a_date': (a or {}).get('event_date', '') if a else '',
            'system_b_date': (b or {}).get('recorded_on', '') if b else '',
            'system_a_location': (a or {}).get('location_id', '') if a else '',
            'system_b_location': (b or {}).get('location_id', '') if b else '',
            'detail': detail,
        })
    # group entries by normalized reference, but keep all rows so duplicates are not lost
    for b in b_rows:
        key = normalize_ref(b.get('record_ref'))
        b_groups.setdefault(key, []).append(b)
    # System A records: missing entries, duplicates, and comparisons
    for a in a_rows:
        key = normalize_ref(a.get('record_id'))
        entries = b_groups.get(key, [])
        if not entries:
            item('Missing in System B', key, a, None, a.get('location_id'))
            continue
        if len(entries) > 1:
            for duplicate in entries:
                item('Duplicate in System B', key, a, duplicate, a.get('location_id'), f'{len(entries)} entries reference this record')
        # Compare every matching entry to A; duplicate entries are independently surfaced
        for b in entries:
            # Avoid matching across tenant boundaries even if refs happen to collide
            if loc_org.get(str(b.get('location_id', '')).strip()) != loc_org.get(str(a.get('location_id', '')).strip()):
                item('Cross-tenant reference', key, a, b, a.get('location_id'), 'System B entry belongs to another tenant; values are not compared')
                continue
            av = safe_decimal(a.get('total_value'))
            bv = safe_decimal(b.get('value'))
            if av is None or bv is None:
                if str(a.get('total_value', '')).strip() != str(b.get('value', '')).strip():
                    item('Invalid or blank value', key, a, b, a.get('location_id'), 'At least one value is not a valid number')
            elif av != bv:
                item('Value mismatch', key, a, b, a.get('location_id'), 'System values differ')
            if str(a.get('event_date', '')).strip() != str(b.get('recorded_on', '')).strip():
                item('Date mismatch', key, a, b, a.get('location_id'), 'Event dates differ')
            if str(a.get('location_id', '')).strip() != str(b.get('location_id', '')).strip():
                item('Location mismatch', key, a, b, a.get('location_id'), 'Location identifiers differ')
    # B entries with invalid refs or refs absent from this tenant's A records
    for b in b_rows:
        key = normalize_ref(b.get('record_ref'))
        matching_a = a_by_norm.get(key)
        if not matching_a:
            # If the record exists in another org, flag boundary mismatch without exposing it.
            other_org_record = next((a for a in system_a if normalize_ref(a.get('record_id')) == key), None)
            reason = 'Cross-tenant reference' if other_org_record else 'Orphan in System B'
            detail = 'Reference points outside this tenant; no System A values exposed' if other_org_record else 'System B references a record that does not exist'
            item(reason, key, None, b, b.get('location_id'), detail)
    return out
