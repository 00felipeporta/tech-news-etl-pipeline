# Tech News ETL Pipeline

A real-time data pipeline built with Python that scrapes tech news, processes raw metadata, and stores the structured output in a PostgreSQL database.

This project focuses on core Data Engineering principles: handling unstructured web data, parsing inconsistent raw inputs, and ensuring reliable database injection.

## How it Works (ETL Flow)

1. **Extract:** Fetches live data from *Hacker News* (`/newest`) using `requests` and parses the HTML tree structure with `BeautifulSoup`.
2. **Transform:** - Extracts global unique identifiers (`noticia_id`) and text content.
   - Converts raw relative timestamps (e.g., "2 hours ago", "5 minutes ago") into standardized `TIMESTAMP` objects using Python's `datetime` module.
   - Includes row-by-row exception handling so the pipeline stays resilient even if the source HTML structure shifts slightly.
3. **Load:** Streams the cleaned data into **PostgreSQL** using `psycopg2`. It implements an `ON CONFLICT DO UPDATE` strategy to handle upserts, making the pipeline idempotent (running it multiple times won't duplicate data).

## Tech Stack
- **Language:** Python 3
- **Libraries:** BeautifulSoup4, Requests, Psycopg2, Datetime
- **Database:** PostgreSQL
- **Environment:** Positron / pgAdmin 4

## Database Schema (`noticias_tech`)
- `noticia_id` (VARCHAR - PRIMARY KEY)
- `titulo` (TEXT)
- `fecha_publicacion` (TIMESTAMP)