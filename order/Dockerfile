FROM python:3.13

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock ./

RUN uv install --system

COPY . .

EXPOSE 80

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
