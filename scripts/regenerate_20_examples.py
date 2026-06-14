from pathlib import Path
import csv, random
from openpyxl import Workbook

base = Path('/Users/dane/workspace/ai-autoingest/samples/current-batch')
base.mkdir(parents=True, exist_ok=True)
random.seed(123)
regions = ['North','South','East','West','Central']
products = ['Cloud','ERP','Security','Analytics','Consulting']
warehouses = ['WH-A','WH-B','WH-C','WH-D']
teams = ['Alpha','Beta','Gamma','Delta']
depts = ['Sales','Finance','HR','Engineering','Support']
months = [f'2026-{m:02d}' for m in range(1, 13)]

csv_names = ['regional_sales.csv','inventory_snapshot.csv','quality_batches.csv','payroll_costs.csv','subscription_metrics.csv','warehouse_turnover.csv','retail_orders.csv','supplier_spend.csv']
for name in csv_names:
    with (base / name).open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['period','region','product','warehouse','revenue_usd','units','defects','cost_usd'])
        for m in months:
            for r in regions:
                for p in products:
                    w.writerow([m,r,p,random.choice(warehouses),random.randint(10000,300000),random.randint(40,2400),random.randint(0,80),random.randint(5000,180000)])

txt_names = ['clinic_queue.txt','hotel_capacity.txt','delivery_operations.txt','support_response.txt']
for name in txt_names:
    lines=[name,'']
    for day in range(1,121):
        lines.append(f'Day {day}: region={random.choice(regions)}, tickets={random.randint(20,500)}, wait_minutes={random.randint(3,95)}, revenue_usd={random.randint(5000,70000)}, occupancy_pct={random.randint(40,98)}, sla_breach={random.randint(0,30)}')
    (base / name).write_text('\n'.join(lines))

md_names = ['department_health.md','marketing_pipeline.md','field_service.md','exam_performance.md']
for name in md_names:
    rows=[f'# {name}','','## Daily details']
    for day in range(1,121):
        rows.append(f'- Day {day}: department={random.choice(depts)}, team={random.choice(teams)}, score={random.randint(60,99)}, target={random.randint(70,95)}, variance={random.randint(-15,15)}, cost_usd={random.randint(3000,40000)}, revenue_usd={random.randint(8000,100000)}')
    (base / name).write_text('\n'.join(rows))

html_names = ['campaign_overview.html','route_metrics.html','product_portfolio.html','customer_mix.html']
for name in html_names:
    trs=[]
    for i in range(1,121):
        trs.append(f"<tr><td>{months[(i-1)%12]}</td><td>{random.choice(regions)}</td><td>{random.choice(products)}</td><td>{random.randint(10000,180000)}</td><td>{random.randint(40,2000)}</td><td>{random.randint(0,60)}</td></tr>")
    html = '<html><body><h1>Dashboard</h1><table border="1"><tr><th>Period</th><th>Region</th><th>Product</th><th>Revenue</th><th>Units</th><th>Defects</th></tr>' + ''.join(trs) + '</table></body></html>'
    (base / name).write_text(html)

xlsx_names = ['operations_summary.xlsx','service_quality.xlsx','finance_overview.xlsx','team_output.xlsx']
for name in xlsx_names:
    wb = Workbook(); ws = wb.active; ws.title = 'Data'
    ws.append(['period','team','region','score','target','variance','revenue_usd','cost_usd'])
    for m in months:
        for t in teams:
            for r in regions:
                score = random.randint(60,100); target = random.randint(70,95)
                ws.append([m,t,r,score,target,score-target,random.randint(5000,120000),random.randint(3000,80000)])
    wb.save(base / name)
print('generated 20 examples at', base)
