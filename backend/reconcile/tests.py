from django.test import SimpleTestCase
from .logic import compare_data, normalize_ref


class ReconciliationLogicTests(SimpleTestCase):
    locations = [{'location_id':'L1','org_id':'O1','location_name':'Site 1'}, {'location_id':'L2','org_id':'O2','location_name':'Site 2'}]
    def test_normalizes_messy_references(self):
        self.assertEqual(normalize_ref('1112'), 'REC-1112')
        self.assertEqual(normalize_ref(' rec-1112 '), 'REC-1112')
    def test_missing_system_b_entry(self):
        rows = compare_data([{'record_id':'REC-1','location_id':'L1','total_value':'10','event_date':'2026-01-01'}], [], self.locations, 'O1')
        self.assertEqual([r['reason'] for r in rows], ['Missing in System B'])
    def test_orphan_b_entry(self):
        rows = compare_data([], [{'entry_id':'B1','record_ref':'REC-404','location_id':'L1','value':'9'}], self.locations, 'O1')
        self.assertTrue(any(r['reason']=='Orphan in System B' for r in rows))
    def test_duplicate_b_entries(self):
        a=[{'record_id':'REC-1','location_id':'L1','total_value':'10','event_date':'2026-01-01'}]
        b=[{'entry_id':'B1','record_ref':'REC-1','location_id':'L1','value':'10','recorded_on':'2026-01-01'}, {'entry_id':'B2','record_ref':'1','location_id':'L1','value':'10','recorded_on':'2026-01-01'}]
        rows=compare_data(a,b,self.locations,'O1')
        self.assertTrue(any(r['reason']=='Duplicate in System B' for r in rows))
    def test_value_mismatch(self):
        a=[{'record_id':'REC-1','location_id':'L1','total_value':'10','event_date':'2026-01-01'}]
        b=[{'entry_id':'B1','record_ref':'1','location_id':'L1','value':'11','recorded_on':'2026-01-01'}]
        rows=compare_data(a,b,self.locations,'O1')
        self.assertTrue(any(r['reason']=='Value mismatch' for r in rows))
    def test_tenant_scope(self):
        a=[{'record_id':'REC-1','location_id':'L1','total_value':'10','event_date':'2026-01-01'}, {'record_id':'REC-2','location_id':'L2','total_value':'20','event_date':'2026-01-01'}]
        b=[{'entry_id':'B1','record_ref':'REC-2','location_id':'L2','value':'20','recorded_on':'2026-01-01'}]
        rows=compare_data(a,b,self.locations,'O1')
        self.assertFalse(any(r['record_id']=='REC-2' and r['system_a_value'] for r in rows))
