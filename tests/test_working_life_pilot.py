import copy
import importlib.util
import json
import csv
import io
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot', ROOT/'scripts/build_working_life_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)

class PilotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(pilot.DATA.read_text())

    def test_recorded_source_values_and_percentage_point_changes(self):
        pilot.validate(self.data)
        self.assertEqual([(r['value'], r['published_yoy_change_pp']) for r in self.data['indicators']],[(49.0,-0.5),(8.3,-0.4),(29.7,3.0),(53.5,-0.7),(15.3,-1.0)])
        self.assertEqual(self.data['source']['bulletin_id'],'57996')
        self.assertEqual(self.data['year'],2025)
        self.assertEqual(self.data['source']['release_date'],'2026-03-25')

    def test_invalid_observations_fail(self):
        for value in (-1,101,float('nan'),float('inf'),True,'49'):
            data = copy.deepcopy(self.data)
            data['indicators'][0]['value'] = value
            with self.assertRaises(ValueError): pilot.validate(data)

    def test_scoring_and_synthetic_status_cannot_be_introduced(self):
        for key,value in [('index_score',50),('rank',1),('status','synthetic-demo')]:
            data=copy.deepcopy(self.data);data[key]=value
            with self.assertRaises(ValueError): pilot.validate(data)
        data=copy.deepcopy(self.data);data['indicators'][0]['included_in_composite']=True
        with self.assertRaises(ValueError): pilot.validate(data)

    def test_missing_provenance_duplicate_ids_and_wrong_period_fail(self):
        for action in ('source','duplicate','year','unit'):
            data=copy.deepcopy(self.data)
            if action=='source': data['source']['url']=''
            if action=='duplicate': data['indicators'][1]['id']='WL-01'
            if action=='year': data['indicators'][0]['comparison_year']=2023
            if action=='unit': data['indicators'][0]['unit']='index points'
            with self.assertRaises(ValueError): pilot.validate(data)

    def test_exports_preserve_provenance_and_do_not_reconstruct_prior_values(self):
        rows=list(csv.DictReader(io.StringIO(pilot.csv_text(self.data))))
        self.assertEqual(len(rows),5)
        self.assertTrue(all(r['data_status']=='official-release-snapshot' and r['included_in_composite']=='false' for r in rows))
        self.assertTrue(all(r['observation_year']=='2025' and r['source_bulletin_id']=='57996' for r in rows))
        self.assertTrue(all(r['source_series_id']=='' for r in rows))
        self.assertIn('not index scores',pilot.panel(self.data))

    def test_generated_outputs_match_reviewed_snapshot(self):
        for path,text in pilot.outputs(self.data).items():
            self.assertEqual(path.read_text(),text,str(path))

if __name__=='__main__':unittest.main()
