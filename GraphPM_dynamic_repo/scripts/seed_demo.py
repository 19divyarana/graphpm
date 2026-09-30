import csv
from pathlib import Path
import requests
BASE='http://localhost:8000/api'
ROOT=Path(__file__).resolve().parents[1]
for name, endpoint in [('projects','projects'),('developers','developers'),('tasks','tasks'),('dependencies','dependencies'),('defects','defects')]:
    with open(ROOT/'data'/f'{name}.csv', newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            r=requests.post(f'{BASE}/{endpoint}', json=row, timeout=20)
            if r.status_code>=400: print(name,row,r.text)
print(requests.post(f'{BASE}/sync-graph').json())
