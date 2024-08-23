---
title: "{{ book.title }}"
type: "Book"
{% if book.authors %}authors:
{% for author in book.authors %}  - "{{ author.name }}"
{% endfor %}{% endif %}
{%- if book.number_of_pages -%}number_of_pages: {{ book.number_of_pages }}
{% endif %}
{%- if book.google_book_id -%}google_book: "{{ book.google_book_id }}"
{% endif %}
{%- if book.openlibrary_book_id -%}openlibrary_book: "{{ book.openlibrary_book_id }}"{% endif %}
isbn_13: "{{ book.isbn }}"
---

{% if book.cover_url %}![{{ book.title }}]({{ book.cover_url }}){% endif %}

{% if book.description %}{{ book.description }}{% endif %}
