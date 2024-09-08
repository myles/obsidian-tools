---
title: "{{ tv_show.name }}"
type: "TV Show"
tmdb_id: {{ tv_show.tmdb_id }}
---

![{{ tv_show.name }}]({{ tv_show.cover_url }})

{{ tv_show.description }}

# Episodes

{% for season in tv_show.seasons %}## {{ season.name }}

{% for episode in season.episodes %}- **Episode {{ episode.episode_number }}**: {{ episode.name }} ^S{{ season.season_number }}E{{ episode.episode_number }}
{% endfor %}
{% endfor %}
