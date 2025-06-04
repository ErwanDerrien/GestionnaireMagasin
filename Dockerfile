FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install sqlalchemy pylint pytest

CMD ["python3", "-m", "src.Controller.store_manager"]