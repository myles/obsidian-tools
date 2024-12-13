---
title: "{{ video_game.title }}"
type: "Video Game"{% if video_game.igdb_id %}
igdb_id: {{ video_game.igdb_id }}{% endif %}{% if video_game.steam_id %}
steam_id: {{ video_game.steam_id }}{% endif %}
---

![{{ video_game.title }}]({{ video_game.cover_url}})

{{ video_game.description }}
