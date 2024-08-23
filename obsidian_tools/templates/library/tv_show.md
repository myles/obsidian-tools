---
title: "{{ tv_series.name }}"
type: "TV Show"
tmdb_id: {{ tv_series.id }}
---

![{{ tv_series.name }}](https://image.tmdb.org/t/p/original{{ tv_series.poster_path }})

{{ tv_series.overview }}

# Episodes

{% for season in tv_seasons %}## {{ season.name }}

{% for episode in season.episodes %}- **Episode {{ episode.episode_number }}**: {{ episode.name }} ^S{{ season.season_number }}E{{ episode.episode_number }}
{% endfor %}
{% endfor %}
