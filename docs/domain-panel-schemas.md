# Domain Panel Schemas

## Goal
Chuẩn hóa dữ liệu backend trả về cho `result` page theo 2 domain chính:
- `game_analytics`
- `project_health`

Cả 2 domain dùng chung 7 panel UI:
1. Executive Summary
2. Phân tích dữ liệu từ file
3. Các metric nhận dạng được từ file
4. Bảng dữ liệu về những data được ghi nhận
5. Raw data text + raw table
6. Metric/data tương ứng
7. JSON kỹ thuật

---

## Common Envelope

```json
{
  "domain": "game_analytics | project_health | generic",
  "confidence": 0.95,
  "file_info": {
    "file_name": "string",
    "file_type": "csv|xlsx|html|txt|md|pdf",
    "file_size": 12345,
    "created_at": "2026-06-14T17:00:00+07:00"
  },
  "panels": {
    "executive_summary": {},
    "file_analysis": {},
    "recognized_metrics": {},
    "recognized_table": {},
    "raw_data": {},
    "structured_output": {},
    "technical_json": {}
  }
}
```

---

# 1) Game Analytics Schema

```json
{
  "domain": "game_analytics",
  "confidence": 0.97,
  "file_info": {
    "file_name": "game_kpi_june.xlsx",
    "file_type": "xlsx",
    "file_size": 48291,
    "created_at": "2026-06-14T17:00:00+07:00"
  },
  "panels": {
    "executive_summary": {
      "headline": "Game giữ DAU ổn định nhưng D7 retention còn thấp.",
      "summary_points": [
        "DAU tăng 6.2% WoW.",
        "ARPDAU tăng nhờ payer conversion tốt hơn.",
        "Crash rate đang cao trên Android low-end devices.",
        "Level 7 có drop-off bất thường."
      ]
    },
    "file_analysis": {
      "dataset_type": "player activity + monetization + retention",
      "time_coverage": "2026-05-01 → 2026-05-31",
      "grain": "daily",
      "entity_count": {
        "players": 148230,
        "sessions": 982144,
        "transactions": 12870
      },
      "dimensions": ["date", "country", "platform", "campaign", "level"],
      "measures": ["dau", "sessions", "revenue", "retention_d1", "retention_d7", "crash_rate"],
      "analysis_note": "Dataset đủ để đánh giá tăng trưởng, retention, monetization và stability."
    },
    "recognized_metrics": {
      "acquisition": ["installs", "new_users", "returning_users"],
      "engagement": ["dau", "mau", "sessions_per_user", "avg_session_length"],
      "retention": ["d1_retention", "d7_retention", "d30_retention", "churn_rate"],
      "monetization": ["revenue", "arpdau", "arppu", "payer_conversion", "ltv"],
      "stability": ["crash_rate", "anr_rate", "load_time"]
    },
    "recognized_table": {
      "columns": [
        {"key": "date", "label": "Date", "type": "date"},
        {"key": "platform", "label": "Platform", "type": "string"},
        {"key": "country", "label": "Country", "type": "string"},
        {"key": "dau", "label": "DAU", "type": "number"},
        {"key": "revenue", "label": "Revenue", "type": "currency"},
        {"key": "arpdau", "label": "ARPDAU", "type": "currency"},
        {"key": "d1_retention", "label": "D1 Retention", "type": "percent"},
        {"key": "crash_rate", "label": "Crash Rate", "type": "percent"}
      ],
      "rows": []
    },
    "raw_data": {
      "raw_text": "...",
      "headers": ["date", "platform", "country", "dau", "revenue"],
      "rows": []
    },
    "structured_output": {
      "user_metrics": {
        "dau": 52144,
        "mau": 238200,
        "new_users": 8200,
        "returning_users": 43944
      },
      "retention_metrics": {
        "d1_retention": 0.41,
        "d7_retention": 0.17,
        "d30_retention": 0.06,
        "churn_rate": 0.22
      },
      "monetization_metrics": {
        "revenue": 128420.55,
        "arpdau": 2.46,
        "arppu": 18.22,
        "payer_conversion": 0.135,
        "ltv": 9.18
      },
      "engagement_metrics": {
        "sessions_per_user": 3.8,
        "avg_session_length_min": 18.4,
        "playtime_hours": 16022.8
      },
      "quality_metrics": {
        "crash_rate": 0.019,
        "anr_rate": 0.004,
        "load_time_sec": 4.8
      },
      "chart_data": {
        "dau_trend": {
          "type": "line",
          "labels": ["2026-05-01", "2026-05-02"],
          "series": [{"name": "DAU", "values": [50200, 51400]}]
        },
        "revenue_by_country": {
          "type": "bar",
          "labels": ["US", "JP", "KR"],
          "series": [{"name": "Revenue", "values": [42000, 28000, 19000]}]
        },
        "retention_curve": {
          "type": "line",
          "labels": ["D1", "D3", "D7", "D14", "D30"],
          "series": [{"name": "Retention", "values": [0.41, 0.28, 0.17, 0.11, 0.06]}]
        }
      }
    },
    "technical_json": {}
  }
}
```

---

# 2) Project Health Schema

```json
{
  "domain": "project_health",
  "confidence": 0.96,
  "file_info": {
    "file_name": "project_portfolio_q2.pdf",
    "file_type": "pdf",
    "file_size": 98231,
    "created_at": "2026-06-14T17:00:00+07:00"
  },
  "panels": {
    "executive_summary": {
      "headline": "Dự án hoàn thành 68% nhưng đang chậm 9 ngày so với kế hoạch.",
      "summary_points": [
        "Milestone Alpha đúng hạn, Beta trễ.",
        "Budget burn cao hơn forecast 7.4%.",
        "Blocked tasks tập trung ở integration.",
        "Có 3 rủi ro mức critical cần xử lý ngay."
      ]
    },
    "file_analysis": {
      "dataset_type": "project progress + budget + risk register",
      "time_coverage": "Q2 2026",
      "grain": "weekly",
      "entity_count": {
        "tasks": 482,
        "milestones": 12,
        "risks": 34,
        "owners": 18
      },
      "dimensions": ["team", "owner", "sprint", "phase", "priority", "status"],
      "measures": ["progress_pct", "planned_cost", "actual_cost", "delay_days", "risk_score"],
      "analysis_note": "Dataset đủ để đánh giá tiến độ, ngân sách, execution và risk health."
    },
    "recognized_metrics": {
      "progress": ["percent_complete", "tasks_completed", "overdue_tasks", "milestone_completion"],
      "schedule": ["schedule_variance", "cycle_time", "lead_time", "blocked_time"],
      "cost": ["planned_cost", "actual_cost", "cost_variance", "burn_rate"],
      "execution": ["velocity", "throughput", "wip"],
      "risk_quality": ["open_risks", "critical_risks", "defect_count", "test_pass_rate"]
    },
    "recognized_table": {
      "columns": [
        {"key": "milestone", "label": "Milestone", "type": "string"},
        {"key": "owner", "label": "Owner", "type": "string"},
        {"key": "status", "label": "Status", "type": "string"},
        {"key": "progress_pct", "label": "Progress %", "type": "percent"},
        {"key": "delay_days", "label": "Delay Days", "type": "number"},
        {"key": "planned_cost", "label": "Planned Cost", "type": "currency"},
        {"key": "actual_cost", "label": "Actual Cost", "type": "currency"},
        {"key": "risk_score", "label": "Risk Score", "type": "number"}
      ],
      "rows": []
    },
    "raw_data": {
      "raw_text": "...",
      "headers": ["milestone", "owner", "status", "progress_pct"],
      "rows": []
    },
    "structured_output": {
      "progress_metrics": {
        "percent_complete": 0.68,
        "tasks_completed": 329,
        "overdue_tasks": 41,
        "milestone_completion": 0.58
      },
      "schedule_metrics": {
        "schedule_variance_days": -9,
        "cycle_time_days": 6.2,
        "lead_time_days": 11.4,
        "blocked_time_days": 2.1
      },
      "cost_metrics": {
        "planned_cost": 420000,
        "actual_cost": 451080,
        "cost_variance": -31080,
        "burn_rate_weekly": 28190
      },
      "execution_metrics": {
        "velocity": 43,
        "throughput": 38,
        "wip": 27
      },
      "risk_metrics": {
        "open_risks": 34,
        "critical_risks": 3,
        "defect_count": 21,
        "test_pass_rate": 0.91
      },
      "chart_data": {
        "progress_trend": {
          "type": "line",
          "labels": ["W1", "W2", "W3", "W4"],
          "series": [{"name": "Progress %", "values": [0.38, 0.47, 0.59, 0.68]}]
        },
        "budget_vs_actual": {
          "type": "bar",
          "labels": ["Planned", "Actual"],
          "series": [{"name": "Budget", "values": [420000, 451080]}]
        },
        "risk_breakdown": {
          "type": "pie",
          "labels": ["Low", "Medium", "High", "Critical"],
          "series": [{"name": "Risks", "values": [12, 11, 8, 3]}]
        }
      }
    },
    "technical_json": {}
  }
}
```

---

## Implementation Note
Backend có thể:
1. classify domain trước
2. route sang `game_analytics` hoặc `project_health`
3. tạo `structured_output` + `recognized_table`
4. AI chỉ viết `executive_summary` + `file_analysis.analysis_note`
