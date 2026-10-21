import csv
from pathlib import Path

def generate(root='fixtures'):
    p=Path(root);p.mkdir(parents=True,exist_ok=True)
    rows=[{'date':f'2026-01-{d:02d}','source':'synthetic-store','metric':m,'value':str(v)}
          for d in range(1,8) for m,v in [('visits',100+d),('pageviews',200+d*2)]]
    for filename,data in [('expected.csv',rows),('matching.csv',rows)]:
        write(p/filename,data)
    broken=[dict(r) for r in rows[:-1]]
    broken[1]['value']='0'
    broken.append({'date':'2026-01-08','source':'synthetic-store','metric':'visits','value':'8'})
    write(p/'broken.csv',broken)
def write(path,rows):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['date','source','metric','value']);w.writeheader();w.writerows(rows)
if __name__=='__main__': generate()
