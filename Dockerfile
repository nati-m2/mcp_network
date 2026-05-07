FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install fastmcp

# Install project dependencies first (better layer caching)
COPY pyproject.toml ./
RUN pip install .

# Copy the rest of the source code
COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
