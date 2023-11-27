# WEA - todo app

## Technologie

- server-side rendering HTML šablon, reaktivní frontend na bázi AJAXU a REST komunikace
    - backend: Python, Flask
    - frontend: [HTMX](https://htmx.org/)

## Návrh aplikace

- model **Task**
    - int id (auto-increment, primary key)
    - int user_id (foreign key)
    - string name
    - string content
    - boolean completed
    - datetime completed_at (nullable)
    - datetime created_at
    - datetime updated_at
- model **User**
    - int id (auto-increment, primary key)
    - string name
    - string password (zahashované)
    - datetime created_at
    - datetime updated_at
- routy aplikace
    - GET `/` - home routa, výchzí bod
    - GET `/tasks/{format=html}` - získá seznam všech úkolů
    - POST `/crete-task` - vytvoří nový úkol
    - PUT `/update-task/{id}` - aktualizuje úkol
    - DELETE `/delete-task/{id}` - smaže úkol

## Poznatky
- databázi pravděpodobně přes SQLite
- možná nějaký příkaz na vytvoření uživatelů a prázdné tabulky úkolů ("migrace-like")

## TODO
- vymyslet systém uživatelů