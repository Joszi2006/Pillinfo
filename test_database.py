# check_dosing_chart.py (in project root)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.api.dependencies import get_drug_database

db = get_drug_database()

# Check dosing chart
chart = db.get_dosing_chart('731531')
print(f'Dosing chart rows: {len(chart)}')

for i, row in enumerate(chart):
    print(f'\nRow {i}:')
    for key, value in row.items():
        print(f'  {key}: {value}')