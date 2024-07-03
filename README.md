# url-shortener

CoinGecko Dev Test - URL Shortener

## Deployment Link

<https://url-shortener-6jx1.onrender.com>

## Implementation

- Python FastAPI serving HTML
- PostgreSQL as the database
- Containerised for deployment with Docker
- CI is done with Github Actions, which runs the unit tests

## How to run

- Initialise the DB with docker-compose:

```bash
docker-compose up -d
```

- Initialise a venv:

```bash
python3 -m venv venv
```

- Activate the venv:

```bash
source venv/bin/activate
```

or for windows

```bash
venv/Scripts/activate
```

- Install the requirements:

```bash
pip install -r requirements.txt
```

- To run the server

```bash
uvicorn app.main:app --reload
```

## Migrations

- If you've made any changes to the models, you can run the following command to generate a new migration:

```bash
alembic revision --autogenerate -m "migration message"
```

- Migrations are also automatically applied on server start

- But if you want to apply the migration manually:

```bash
alembic upgrade head
```

## Tests

- All you need to do to run is `pytest`

## Notes

- Python is fussy with the relative imports, so it is best to use absolute imports. e.g. `from app.database import ..` instead of `from ..database import ..`
