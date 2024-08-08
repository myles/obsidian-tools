---
type: "Monthly Log"
---

# Days
{% for weekly_log, items in days_in_month|groupby("weekly_log") %}
## {{ weekly_log }}{% for item in items %}
### [[{{ item.day|date("YYYY-MM-DD") }}|{{ item.day|date("Do MMMM, YYYY") }}]]
{%- endfor -%}
{%- endfor -%}
