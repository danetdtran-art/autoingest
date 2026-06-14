from pathlib import Path
import csv, random
from openpyxl import Workbook

base = Path('/Users/dane/workspace/ai-autoingest/samples')
base.mkdir(parents=True, exist_ok=True)
random.seed(7)

students = [
    'An','Binh','Chi','Dung','Giang','Hanh','Hoa','Hung','Khanh','Linh',
    'Long','Mai','Minh','Nam','Ngoc','Phuong','Quan','Trang','Tuan','Vy'
]
subjects = ['Math','Literature','English','Physics','Chemistry','Biology']

# 33 exam scores csv
with (base / '33_exam_scores_semester.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['student_id','student_name','class','math','literature','english','physics','chemistry','biology'])
    for i, s in enumerate(students, 1):
        scores = [round(random.uniform(5.0, 9.9), 1) for _ in range(6)]
        w.writerow([f'ST{i:03d}', s, '12A1' if i <= 10 else '12A2', *scores])

# 34 clinic visits txt
lines = ['Clinic Visit Log - April 2026', '']
for i in range(1, 61):
    age = random.randint(6, 82)
    wait = random.randint(5, 95)
    fee = random.randint(120000, 950000)
    dept = random.choice(['General','Pediatrics','ENT','Cardio','Dental'])
    outcome = random.choice(['treated','follow_up','lab_test','referred'])
    lines.append(f'Visit {i}: patient=P{i:03d}, age={age}, department={dept}, wait_minutes={wait}, fee_vnd={fee}, outcome={outcome}')
(base / '34_clinic_visits_april.txt').write_text('\n'.join(lines))

# 35 supermarket sales md
rows = ['# Supermarket Daily Sales Summary', '', '## Transactions']
for d in range(1, 31):
    rev = random.randint(25000000, 98000000)
    orders = random.randint(180, 620)
    basket = random.randint(120000, 380000)
    rows.append(f'- Day {d}: revenue_vnd={rev}, orders={orders}, avg_basket_vnd={basket}, returns={random.randint(2,18)}')
(base / '35_supermarket_sales_monthly.md').write_text('\n'.join(rows))

# 36 warehouse inventory html
trs = []
for i in range(1, 51):
    trs.append(f"<tr><td>SKU{i:03d}</td><td>{random.choice(['North','South','East','West'])}</td><td>{random.randint(50,3000)}</td><td>{random.randint(40,3200)}</td><td>{random.randint(100000,3500000)}</td></tr>")
html = '<html><body><h1>Warehouse Inventory Snapshot</h1><table border="1"><tr><th>SKU</th><th>Warehouse</th><th>Expected</th><th>Counted</th><th>Value VND</th></tr>' + ''.join(trs) + '</table></body></html>'
(base / '36_warehouse_inventory_snapshot.html').write_text(html)

# 37 payroll csv
with (base / '37_payroll_department_may.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['employee_id','department','base_salary_vnd','bonus_vnd','overtime_hours','deduction_vnd'])
    for i in range(1, 71):
        w.writerow([f'EMP{i:03d}', random.choice(['Sales','Engineering','HR','Finance','Support']), random.randint(9000000,42000000), random.randint(0,12000000), random.randint(0,45), random.randint(200000,3500000)])

# 38 delivery performance xlsx
wb = Workbook()
ws = wb.active
ws.title = 'Delivery'
ws.append(['order_id','region','delivery_minutes','sla_minutes','status','shipping_fee_vnd'])
for i in range(1, 121):
    sla = random.choice([30,45,60,90])
    actual = max(10, int(random.gauss(sla, 18)))
    ws.append([f'OD{i:04d}', random.choice(['HCM','HN','DN','CT']), actual, sla, 'on_time' if actual <= sla else 'late', random.randint(15000,85000)])
wb.save(base / '38_delivery_performance_weekly.xlsx')

# 39 hotel occupancy txt
lines = ['Hotel Occupancy and Revenue Report', '']
for d in range(1, 32):
    rooms = 120
    occupied = random.randint(58, 118)
    adr = random.randint(650000, 2400000)
    cancel = random.randint(0, 12)
    lines.append(f'Day {d}: total_rooms={rooms}, occupied_rooms={occupied}, occupancy_pct={round(occupied/rooms*100,1)}, adr_vnd={adr}, cancellations={cancel}')
(base / '39_hotel_occupancy_report.txt').write_text('\n'.join(lines))

# 40 support tickets md
rows = ['# Customer Support Ticket Overview', '', '## Tickets']
for i in range(1, 81):
    rows.append(f'- Ticket {i}: channel={random.choice(["email","chat","phone"])}, priority={random.choice(["low","medium","high"])}, resolution_hours={round(random.uniform(0.5, 48.0),1)}, csat={random.randint(1,5)}')
(base / '40_support_ticket_overview.md').write_text('\n'.join(rows))

# 41 marketing campaign html
trs = []
for i in range(1, 26):
    spend = random.randint(3000000, 95000000)
    clicks = random.randint(1500, 42000)
    leads = random.randint(40, 1800)
    conv = random.randint(10, leads)
    trs.append(f"<tr><td>Campaign {i}</td><td>{spend}</td><td>{clicks}</td><td>{leads}</td><td>{conv}</td></tr>")
html = '<html><body><h1>Marketing Campaign Performance</h1><table border="1"><tr><th>Campaign</th><th>Spend VND</th><th>Clicks</th><th>Leads</th><th>Conversions</th></tr>' + ''.join(trs) + '</table></body></html>'
(base / '41_marketing_campaign_performance.html').write_text(html)

# 42 manufacturing qc csv
with (base / '42_manufacturing_qc_batch.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['batch_id','line','units_produced','defect_units','rework_units','downtime_minutes'])
    for i in range(1, 55):
        produced = random.randint(800, 8200)
        defect = random.randint(0, int(produced * 0.08))
        rework = random.randint(0, defect)
        downtime = random.randint(0, 130)
        w.writerow([f'B{i:03d}', random.choice(['L1','L2','L3','L4']), produced, defect, rework, downtime])

print('generated 10 practical samples')
