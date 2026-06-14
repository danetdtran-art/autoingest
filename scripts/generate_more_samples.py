from pathlib import Path
import csv, random, json
from datetime import date, timedelta

base = Path('/Users/dane/workspace/ai-autoingest/samples')
base.mkdir(parents=True, exist_ok=True)
random.seed(42)

regions = ['North America','Europe','Asia Pacific','LATAM','Middle East']
products = ['Cloud Services','Enterprise Software','Consulting','Security','Analytics']
departments = ['Sales','Engineering','HR','Finance','Support','Marketing','Operations']
warehouses = ['North Hub','East Hub','South Hub','West Hub','Central Hub']
teams = ['Alpha','Beta','Gamma','Delta','Omega']
months = ['2025-01','2025-02','2025-03','2025-04','2025-05','2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12']

# 1-8 csv
for idx in range(13, 21):
    path = base / f'{idx:02d}_rich_dataset_{idx}.csv'
    with path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['period','region','product_line','revenue_usd','units_sold','growth_pct','cogs_usd','headcount'])
        for m in months:
            for r in regions:
                for p in products[:4]:
                    revenue = random.randint(300000, 4200000)
                    units = random.randint(40, 3200)
                    growth = round(random.uniform(-3.5, 34.5), 1)
                    cogs = int(revenue * random.uniform(0.35, 0.72))
                    headcount = random.randint(8, 120)
                    w.writerow([m, r, p, revenue, units, growth, cogs, headcount])

# 9-12 txt
for idx in range(21, 25):
    path = base / f'{idx:02d}_ops_report_{idx}.txt'
    lines = [f'Operations Performance Report {idx}', '']
    for i, wh in enumerate(warehouses, 1):
        lines.append(f'Warehouse: {wh}')
        for d in range(1, 31):
            sku = 1000 + i*100 + d
            counted = random.randint(800, 4200)
            expected = counted + random.randint(-120, 120)
            shrink = random.randint(0, 9000)
            lines.append(f'Day {d}: sku={sku}, expected={expected}, counted={counted}, variance={counted-expected}, shrinkage_usd={shrink}')
        lines.append('')
    path.write_text('\n'.join(lines))

# 13-16 md
for idx in range(25, 29):
    path = base / f'{idx:02d}_people_summary_{idx}.md'
    rows = [f'# Workforce Planning Summary {idx}', '', '## Department overview']
    for dep in departments:
        hc = random.randint(18, 340)
        active = hc - random.randint(0, 18)
        open_roles = random.randint(0, 25)
        attr = round(random.uniform(0.5, 18.0), 1)
        rows.append(f'- {dep}: headcount={hc}, active={active}, open_roles={open_roles}, attrition_pct={attr}')
    rows += ['', '## Team notes']
    for t in teams:
        rows.append(f'- Team {t}: engagement_score={random.randint(68, 96)}, delivery_score={random.randint(70, 99)}, training_hours={random.randint(120, 1600)}')
    path.write_text('\n'.join(rows))

# 17-18 html
for idx in range(29, 31):
    path = base / f'{idx:02d}_dashboard_{idx}.html'
    rows = []
    for m in months:
        for r in regions:
            rows.append(f'<tr><td>{m}</td><td>{r}</td><td>{random.randint(500000,5000000)}</td><td>{random.randint(100,4000)}</td><td>{round(random.uniform(2.0,35.0),1)}%</td></tr>')
    html = f'''<html><body><h1>Executive Dashboard {idx}</h1><table border="1"><tr><th>Month</th><th>Region</th><th>Revenue</th><th>Units</th><th>Growth</th></tr>{''.join(rows)}</table></body></html>'''
    path.write_text(html)

# 19-20 xlsx via openpyxl
from openpyxl import Workbook
for idx in range(31, 33):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Metrics'
    ws.append(['month','team','kpi','score','target','variance','revenue_usd','cost_usd'])
    for m in months:
        for t in teams:
            for kpi in ['delivery','quality','satisfaction','retention']:
                score = random.randint(70, 100)
                target = random.randint(75, 98)
                variance = score - target
                revenue = random.randint(150000, 2100000)
                cost = random.randint(50000, 900000)
                ws.append([m, t, kpi, score, target, variance, revenue, cost])
    wb.save(base / f'{idx:02d}_kpi_workbook_{idx}.xlsx')

print('generated 20 files')
