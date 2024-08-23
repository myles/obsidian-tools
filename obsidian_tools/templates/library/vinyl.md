---
title: "{{ vinyl.title }}{% if vinyl.artists %} — {{ vinyl.display_artists }}{% endif %}"
type: "Vinyl"
{% if vinyl.artists %}artists:
{% for artist in vinyl.artists %}  - "{{ artist.name }}"
{% endfor %}{%- endif -%}
discogs_id: {{ vinyl.discogs_id }}
isbn_13: "{{ vinyl.isbn }}"
---

{% if vinyl.image_url %}![{{ vinyl.title }}{% if vinyl.artists %} — {{ vinyl.display_artists }}{% endif %}]({{ vinyl.image_url }}){% endif %}

{% if vinyl.tracklist %}
## Track list
{% for position, items in vinyl.tracklist|groupby("position") %}
### Side {{ position }}
{% for item in items %}
- {{ item.title }}{% if item.duration %} ({{ item.duration }}){% endif %}
{% endfor %}
{% endfor %}
{% endif %}