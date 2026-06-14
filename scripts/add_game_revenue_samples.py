from pathlib import Path
import csv, random

base = Path('/Users/dane/workspace/ai-autoingest/samples/current-batch')
base.mkdir(parents=True, exist_ok=True)
random.seed(777)

# 1) game model revenue
with (base / 'game_model_revenue.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['period','game_mode','region','matches_played','active_players','iap_revenue_usd','ad_revenue_usd','battlepass_revenue_usd','total_revenue_usd'])
    for month in [f'2026-{m:02d}' for m in range(1, 13)]:
        for mode in ['Ranked','Casual','Arcade','Tournament']:
            for region in ['NA','EU','SEA','LATAM','MENA']:
                iap = random.randint(8000, 120000)
                ad = random.randint(2000, 45000)
                bp = random.randint(3000, 65000)
                total = iap + ad + bp
                w.writerow([month, mode, region, random.randint(5000, 120000), random.randint(2000, 50000), iap, ad, bp, total])

# 2) mobile game revenue
with (base / 'mobile_game_revenue.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['date','platform','country','dau','payers','sessions','arpdau_usd','iap_revenue_usd','ad_revenue_usd','subscription_revenue_usd','total_revenue_usd'])
    for month in range(1, 13):
        for day in range(1, 29):
            date = f'2026-{month:02d}-{day:02d}'
            for platform in ['iOS','Android']:
                for country in ['US','JP','KR','BR','VN']:
                    dau = random.randint(5000, 150000)
                    payers = random.randint(200, max(300, dau // 8))
                    iap = random.randint(5000, 180000)
                    ad = random.randint(2000, 80000)
                    sub = random.randint(1000, 45000)
                    total = iap + ad + sub
                    arpdau = round(total / dau, 4)
                    w.writerow([date, platform, country, dau, payers, random.randint(8000, 220000), arpdau, iap, ad, sub, total])

print('added game revenue samples')
print(base / 'game_model_revenue.csv')
print(base / 'mobile_game_revenue.csv')
