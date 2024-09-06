---
title: "{{ month.start|format_date("MMMM YYYY") }}"
type: Monthly Log
aliases:
  - "{{ month.start|format_date("MMMM YYYY") }}"
---

[[{{ month.prev_month_start|format_date("YYYY-MM") }}|{{ month.prev_month_start|format_date("MMMM YYYY") }}]] - **{{ month.prev_month_start|format_date("MMMM YYYY") }}** - [[{{ month.next_month_start|format_date("YYYY-MM") }}|{{ month.next_month_start|format_date("MMMM YYYY") }}]]

## Days

{% for week in month.weeks %}
### CW{{ week.start|format_date("WW YYYY") }}

  {% for is_weekend, days in week.days|groupby("is_weekend") %}
    {% if is_weekend %}
#### Weekend
    {% else %}
#### Weekdays
    {% endif %}
    {% for day in days %}
##### [[{{ day.note_name }}|{{ day.date|format_date("dddd, Do MMMM, YYYY") }}]]
    {% endfor %}
  {% endfor %}
{% endfor %}
