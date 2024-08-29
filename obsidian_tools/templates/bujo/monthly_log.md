---
title: "{{ start_of_month|format_date("MMMM YYYY") }}"
type: Monthly Log
aliases:
  - "{{ start_of_month|format_date("MMMM YYYY") }}"
---

[[{{ start_of_previous_month|format_date("YYYY-MM") }}|{{ start_of_previous_month|format_date("MMMM YYYY") }}]] - **{{ start_of_previous_month|format_date("MMMM YYYY") }}** - [[{{ start_of_next_month|format_date("YYYY-MM") }}|{{ start_of_next_month|format_date("MMMM YYYY") }}]]

## Days

{% for week_number, week_days in days|groupby("week_number") -%}
### CW{{ week_days[0].date|format_date("WW") }} {{ week_days[0].date|format_date("YYYY") }}
{% for day in week_days -%}
#### [[{{ day.daily_log_file_name }}|{{ day.date|format_date("Do MMMM, YYYY") }}]]
{% endfor %}
{% endfor %}
