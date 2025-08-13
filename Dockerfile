FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install fastmcp

COPY pyproject.toml .
RUN pip install .

EXPOSE 8080

CMD ["python", "main.py"]
