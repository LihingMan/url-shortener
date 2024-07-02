FROM python:3.11-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

ENV DATABASE_URL="postgresql://bryanleepostgres:GnLHmATHXm1B9qgBsHOkXJ4nfP66Jx2I@dpg-cq1ugb2ju9rs73bf0qfg-a.singapore-postgres.render.com/url_shortener_mvvy"

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
