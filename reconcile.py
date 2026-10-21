"""Daily external-source reconciliation; standard library only."""
import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from datetime import date

KEYS = ('date', 'source', 'metric')

def read(path):
    result = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        if not set((*KEYS, 'value')).issubset(reader.fieldnames or []):
            raise ValueError('required columns: date,source,metric,value')
        for row in reader:
            if None in row or any(row.get(k) is None for k in (*KEYS, 'value')):
                raise ValueError('row must contain all declared columns')
            key = tuple(row[k] for k in KEYS)
            if any(v != v.strip() for v in key):
                raise ValueError('key whitespace is not allowed')
            if date.fromisoformat(key[0]).isoformat() != key[0]:
                raise ValueError('date must be YYYY-MM-DD')
            if not all(key) or key in result:
                raise ValueError(f'empty or duplicate key: {key}')
            try:
                val = Decimal(row['value'])
            except InvalidOperation as exc:
                raise ValueError(f'invalid value at {key}') from exc
            if not val.is_finite() or val < 0:
                raise ValueError(f'non-finite or negative value at {key}')
            result[key] = val
    if not result:
        raise ValueError('empty input is not evidence of matching data')
    return result

def compare(expected, actual, absolute=Decimal('0'), relative=Decimal('0')):
    if not absolute.is_finite() or not relative.is_finite() or absolute < 0 or relative < 0:
        raise ValueError('tolerances must be finite and non-negative')
    rows = []
    for key in sorted(expected.keys() | actual.keys()):
        e, a = expected.get(key), actual.get(key)
        status = 'missing_actual' if a is None else 'unexpected_actual' if e is None else 'match'
        delta = None if e is None or a is None else a-e
        if delta is not None and abs(delta) > max(absolute, abs(e)*relative):
            status = 'mismatch'
        rows.append(dict(zip(KEYS,key), expected=None if e is None else str(e),
                         actual=None if a is None else str(a), delta=None if delta is None else str(delta), status=status))
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('expected');p.add_argument('actual');p.add_argument('--output',default='output/report.json')
    p.add_argument('--absolute',default='0');p.add_argument('--relative',default='0')
    args=p.parse_args()
    try:
        rows=compare(read(args.expected),read(args.actual),Decimal(args.absolute),Decimal(args.relative))
    except (ValueError, InvalidOperation, OSError, csv.Error) as exc:
        p.exit(2,str(exc)+'\n')
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rows,indent=2)+'\n')
    bad=sum(r['status']!='match' for r in rows)
    print(f'{len(rows)} keys checked; {bad} discrepancies; {out}')
    return int(bad>0)
if __name__=='__main__':
    raise SystemExit(main())
