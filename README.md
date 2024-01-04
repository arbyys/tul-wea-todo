# WEA - todo app

## Technologie

- server-side rendering HTML šablon, reaktivní frontend na bázi AJAXU a REST komunikace
    - backend: Python, Flask
    - frontend: [HTMX](https://htmx.org/)

## Struktura DB

- model **Task**
    - int id (auto-increment, primary key)
    - int user_id (foreign key)
    - string title
    - string content
    - boolean is_completed
    - datetime created_at
    - datetime updated_at
- model **User**
    - int id (auto-increment, primary key)
    - string username
    - string password (zahashované)
    - boolean has_private_profile
    - datetime created_at
    - datetime updated_at