import tempfile
import unittest
from pathlib import Path
from decimal import Decimal as D
from reconcile import compare,read
from generate import generate
class Checks(unittest.TestCase):
    def test_scenarios(self):
        with tempfile.TemporaryDirectory() as d:
            generate(d);p=Path(d);e=read(p/'expected.csv')
            self.assertTrue(all(x['status']=='match' for x in compare(e,read(p/'matching.csv'))))
            bad=[x['status'] for x in compare(e,read(p/'broken.csv')) if x['status']!='match']
            self.assertCountEqual(bad,['mismatch','missing_actual','unexpected_actual'])
    def test_zero_is_not_missing(self):
        k=('2026-01-01','s','visits')
        self.assertEqual(compare({k:D(0)},{k:D(0)})[0]['status'],'match')
        self.assertEqual(compare({k:D(0)},{})[0]['status'],'missing_actual')
    def test_decimal_tolerances(self):
        k=('2026-01-01','s','revenue')
        self.assertEqual(compare({k:D('0.30')},{k:D('0.31')},D('.01'))[0]['status'],'match')
        self.assertEqual(compare({k:D(100)},{k:D(101)},relative=D('.01'))[0]['status'],'match')
        with self.assertRaises(ValueError):compare({}, {}, D('-1'))
    def test_invalid_input(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv'
            for value in ['NaN','Infinity','-1','oops']:
                p.write_text('date,source,metric,value\n2026-01-01,s,visits,'+value+'\n')
                with self.assertRaises(ValueError):read(p)
            p.write_text('date,source,metric,value\n')
            with self.assertRaises(ValueError):read(p)
    def test_duplicate_key(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv';p.write_text('date,source,metric,value\n'+ '2026-01-01,s,visits,1\n'*2)
            with self.assertRaises(ValueError):read(p)
    def test_cli_contract(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as d:
            generate(d);p=Path(d)
            def run(*args):
                return subprocess.run([sys.executable,'reconcile.py',*map(str,args),'--output',str(p/'out.json')],capture_output=True,text=True)
            self.assertEqual(run(p/'expected.csv',p/'matching.csv').returncode,0)
            self.assertEqual(run(p/'expected.csv',p/'broken.csv').returncode,1)
            for row in ['2026-01-01,s,visits','yesterday,s,visits,1','2026-01-01, s,visits,1','2026-01-01,s,visits,1,extra']:
                bad=p/'invalid.csv';bad.write_text('date,source,metric,value\n'+row+'\n')
                r=run(bad,bad);self.assertEqual(r.returncode,2);self.assertNotIn('Traceback',r.stderr)
            for tol in ['NaN','Infinity','-1','nonsense']:
                r=run(p/'expected.csv',p/'matching.csv','--relative',tol)
                self.assertEqual(r.returncode,2);self.assertNotIn('Traceback',r.stderr)
            r=run(p/'absent.csv',p/'matching.csv');self.assertEqual(r.returncode,2);self.assertNotIn('Traceback',r.stderr)
if __name__=='__main__':unittest.main()

