from pathlib import Path
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

base = Path('/Users/dane/workspace/ai-autoingest/samples/project-metrics')
base.mkdir(parents=True, exist_ok=True)

rows = [
    ['Project Atlas','Platform Revamp','On Track',68,420000,389000,12,3,18],
    ['Project Nova','Billing Upgrade','At Risk',54,310000,336000,21,5,27],
    ['Project Orion','Game Backend','Delayed',47,510000,548000,34,7,39],
    ['Project Zenith','Mobile LiveOps','On Track',73,275000,244000,9,2,14],
    ['Project Pulse','Analytics Pipeline','At Risk',61,190000,205000,16,4,19],
]

# HTML
html = ['<html><body><h1>Project Portfolio Dashboard</h1><table border="1">',
        '<tr><th>Project</th><th>Initiative</th><th>Status</th><th>Progress %</th><th>Planned Cost</th><th>Actual Cost</th><th>Delay Days</th><th>Critical Risks</th><th>Blocked Tasks</th></tr>']
for r in rows:
    html.append('<tr>' + ''.join(f'<td>{v}</td>' for v in r) + '</tr>')
html.append('</table></body></html>')
(base / 'project_portfolio_dashboard.html').write_text('\n'.join(html))

# XLSX
wb = Workbook()
ws = wb.active
ws.title = 'Projects'
ws.append(['project','initiative','status','progress_pct','planned_cost_usd','actual_cost_usd','delay_days','critical_risks','blocked_tasks'])
for r in rows:
    ws.append(r)
wb.save(base / 'project_portfolio_dashboard.xlsx')

# PDF
pdf_path = base / 'project_portfolio_dashboard.pdf'
c = canvas.Canvas(str(pdf_path), pagesize=A4)
width, height = A4
c.setFont('Helvetica-Bold', 16)
c.drawString(40, height - 40, 'Project Portfolio Dashboard')
c.setFont('Helvetica', 10)
y = height - 80
headers = ['Project','Initiative','Status','Progress%','Planned','Actual','Delay','Risks','Blocked']
x_positions = [40,110,220,290,350,410,470,515,555]
for x,h in zip(x_positions, headers):
    c.drawString(x, y, h)
y -= 18
for r in rows:
    vals = [str(r[0]), str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5]), str(r[6]), str(r[7]), str(r[8])]
    for x,v in zip(x_positions, vals):
        c.drawString(x, y, v[:18])
    y -= 16
c.save()

print(base)
print('project_portfolio_dashboard.html')
print('project_portfolio_dashboard.xlsx')
print('project_portfolio_dashboard.pdf')
