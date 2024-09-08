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
## Track list{% for track in vinyl.tracklist %}
- **{{ track.position }}**: {{ track.title }}{% if track.duration %} ({{ track.duration }}){% endif %}{% endfor %}{% endif %}
