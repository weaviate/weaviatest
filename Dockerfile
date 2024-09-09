FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN pip install -e .

ENTRYPOINT ["python", "weaviatest.py"]
