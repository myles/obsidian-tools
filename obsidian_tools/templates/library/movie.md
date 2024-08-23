---
title: "{{ movie.title }}"
type: "Movie"
tmdb_id: {{ movie.id }}
tagline: "{{ movie.tagline }}"
---

![{{ movie.title }}](https://image.tmdb.org/t/p/original{{ movie.poster_path }})

{{ movie.overview }}
