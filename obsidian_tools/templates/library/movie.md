---
title: "{{ movie.title }}"
type: "Movie"
tagline: "{{ movie.tagline }}"
tmdb_id: {{ movie.tmdb_id }}
---

![{{ movie.title }}]({{ movie.cover_url }})

{{ movie.description }}
