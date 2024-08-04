---
name: "{{ book.title }}"
type: "Book"
{% if authors %}authors:{% for author in authors %}
  - "{{ author.name }}"{% endfor %}{% endif %}
number_of_pages: {{ book.number_of_pages }}
isbn_13: "{{ book.isbn_13[0] }}"
---

![{{ book.title }}](https://covers.openlibrary.org/b/olid/{{ book.key.replace("/books/", "") }}-L.jpg)

{{ works[0].description.value }}
