---
title: "CW{{ week.start|format_date("WW YYYY") }}"
type: "Weekly Log"
aliases: 
  - "CW{{ week.start|format_date("WW YYYY") }}"
---

[[{{ week.prev_week_start|format_date("YYYY-WW") }}|CW{{ week.prev_week_start|format_date("WW YYYY") }}]] - **CW{{ week.start|format_date("WW YYYY") }}** - [[{{ week.next_week_start|format_date("YYYY-WW") }}|CW{{ week.next_week_start|format_date("WW YYYY") }}]]

{% for is_weekend, days in week.days|groupby("is_weekend") %}
{% if is_weekend %}
## Weekend
{% else %}
## Weekdays
{% endif %}
{% for day in days %}
### {{ day.date|format_date("dddd") }}, [[{{ day.note_name }}|{{ day.date|format_date("Do MMMM, YYYY") }}]] ^{{ day.date|format_date("YYYY-MM-DD") }}
{% endfor %}
{% endfor %}
