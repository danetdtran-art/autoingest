from pathlib import Path
import csv, random
from openpyxl import Workbook

base = Path('/Users/dane/workspace/ai-autoingest/samples')
base.mkdir(parents=True, exist_ok=True)
random.seed(2026)

regions = ['North','South','East','West','Central']
products = ['Alpha','Beta','Gamma','Delta','Omega']
warehouses = ['WH-A','WH-B','WH-C','WH-D','WH-E']
departments = ['Sales','Engineering','HR','Finance','Support','Marketing']
teams = ['Team A','Team B','Team C','Team D','Team E']
months = [f'2026-{m:02d}' for m in range(1, 13)]
channels = ['email','chat','phone','social']

# 43-48 csv revenue/inventory/payroll/qc
for idx in range(43, 49):
    path = base / f'{idx:02d}_dashboard_revenue_inventory_{idx}.csv'
    with path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['period','region','warehouse','product','revenue_usd','units_sold','inventory_units','defect_units','headcount'])
        for m in months:
            for r in regions:
                for p in products:
                    w.writerow([
                        m, r, random.choice(warehouses), p,
                        random.randint(200000, 5000000),
                        random.randint(50, 3500),
                        random.randint(100, 8000),
                        random.randint(0, 220),
                        random.randint(5, 180)
                    ])

# 49-52 txt operations/support/clinic/hotel
for idx in range(49, 53):
    lines = [f'Operations Dashboard Feed {idx}', '']
    for day in range(1, 121):
        lines.append(
            f'Day {day}: region={random.choice(regions)}, warehouse={random.choice(warehouses)}, '
            f'orders={random.randint(80,1200)}, revenue_usd={random.randint(15000,240000)}, '
            f'wait_minutes={random.randint(3,95)}, defects={random.randint(0,70)}, csat={random.randint(1,5)}'
        )
    (base / f'{idx:02d}_operations_feed_{idx}.txt').write_text('\n'.join(lines))

# 53-56 markdown summaries
for idx in range(53, 57):
    rows = [f'# Business Performance Summary {idx}', '', '## Daily performance']
    for day in range(1, 121):
        rows.append(
            f'- Day {day}: department={random.choice(departments)}, team={random.choice(teams)}, '
            f'score={random.randint(60,99)}, target={random.randint(70,95)}, variance={random.randint(-20,15)}, '
            f'cost_usd={random.randint(5000,55000)}, revenue_usd={random.randint(10000,150000)}'
        )
    (base / f'{idx:02d}_business_summary_{idx}.md').write_text('\n'.join(rows))

# 57-60 html tables
for idx in range(57, 61):
    trs = []
    for i in range(1, 121):
        trs.append(
            f"<tr><td>{months[(i-1)%12]}</td><td>{random.choice(regions)}</td><td>{random.choice(products)}</td>"
            f"<td>{random.randint(20000,300000)}</td><td>{random.randint(50,1600)}</td><td>{random.randint(0,120)}</td></tr>"
        )
    html = '<html><body><h1>Dashboard Table</h1><table border="1"><tr><th>Period</th><th>Region</th><th>Product</th><th>Revenue</th><th>Units</th><th>Defects</th></tr>' + ''.join(trs) + '</table></body></html>'
    (base / f'{idx:02d}_dashboard_table_{idx}.html').write_text(html)

# 61-62 xlsx
for idx in range(61, 63):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Dashboard'
    ws.append(['period','team','channel','tickets','resolution_hours','score','revenue_usd','cost_usd'])
    for m in months:
        for t in teams:
            for c in channels:
                ws.append([
                    m, t, c,
                    random.randint(20,500),
                    round(random.uniform(0.5, 72.0), 1),
                    random.randint(60, 100),
                    random.randint(10000, 120000),
                    random.randint(5000, 80000)
                ])
    wb.save(base / f'{idx:02d}_dashboard_workbook_{idx}.xlsx')

print('generated 20 dashboard samples')
