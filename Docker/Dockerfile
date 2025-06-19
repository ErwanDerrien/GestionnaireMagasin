FROM python:3.11-slim

WORKDIR /app

COPY ./docker/requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ../ .

CMD ["python3", "-m", "src.Controller.store_manager"]