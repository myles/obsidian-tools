{% if book.cover_url %}![{{ book.title }}]({{ book.cover_url }}){% endif %}

{% if book.description %}{{ book.description }}{% endif %}
