from pathlib import Path
import csv, random
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

base = Path('/Users/dane/workspace/ai-autoingest/samples/current-batch')
base.mkdir(parents=True, exist_ok=True)
random.seed(456)

cities = ['HCM','HN','DN','CT','HP']
programs = ['A','B','C','D']
vendors = ['V1','V2','V3','V4']
months = [f'2026-{m:02d}' for m in range(1, 13)]
cats = ['Basic','Pro','Enterprise']

# 5 CSV
csv_names = ['energy_consumption.csv','school_attendance.csv','insurance_claims.csv','farm_yield.csv','telecom_usage.csv']
for name in csv_names:
    with (base / name).open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['period','city','program','value_a','value_b','value_c','cost_usd'])
        for m in months:
            for c in cities:
                for p in programs:
                    w.writerow([m,c,p,random.randint(100,5000),random.randint(10,900),random.randint(0,120),random.randint(1000,40000)])

# 4 TXT
for name in ['airport_operations.txt','restaurant_kitchen.txt','call_center_load.txt','water_supply.txt']:
    lines=[name,'']
    for day in range(1,121):
        lines.append(f'Day {day}: city={random.choice(cities)}, tickets={random.randint(20,700)}, wait_minutes={random.randint(1,120)}, throughput={random.randint(50,3000)}, quality_score={random.randint(60,99)}')
    (base / name).write_text('\n'.join(lines))

# 3 MD
for name in ['nonprofit_programs.md','university_departments.md','construction_updates.md']:
    rows=[f'# {name}','','## Daily report']
    for day in range(1,121):
        rows.append(f'- Day {day}: department={random.choice(programs)}, city={random.choice(cities)}, score={random.randint(60,99)}, target={random.randint(70,95)}, variance={random.randint(-15,15)}, cost_usd={random.randint(2000,30000)}')
    (base / name).write_text('\n'.join(rows))

# 2 HTML
for name in ['tourism_bookings.html','pharmacy_sales.html']:
    trs=[]
    for i in range(1,121):
        trs.append(f"<tr><td>{months[(i-1)%12]}</td><td>{random.choice(cities)}</td><td>{random.choice(cats)}</td><td>{random.randint(1000,90000)}</td><td>{random.randint(10,1500)}</td><td>{random.randint(0,80)}</td></tr>")
    html = '<html><body><h1>Dashboard</h1><table border="1"><tr><th>Period</th><th>City</th><th>Category</th><th>Revenue</th><th>Units</th><th>Returns</th></tr>' + ''.join(trs) + '</table></body></html>'
    (base / name).write_text(html)

# 1 XLSX
wb = Workbook(); ws = wb.active; ws.title = 'Data'
ws.append(['period','vendor','city','score','target','variance','revenue_usd','cost_usd'])
for m in months:
    for v in vendors:
        for c in cities:
            score = random.randint(60,100); target = random.randint(70,95)
            ws.append([m,v,c,score,target,score-target,random.randint(5000,120000),random.randint(3000,80000)])
wb.save(base / 'vendor_performance.xlsx')

print('generated 15 more examples')
