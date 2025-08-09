# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# העתקת קבצי הפרויקט
COPY pyproject.toml .
COPY main.py .
COPY modules ./modules
COPY .env .env

# התקנת התלויות
RUN pip install --upgrade pip
RUN pip install fastmcp
RUN pip install .

# פותח את הפורט 8080
EXPOSE 8080

# הפעלת השרת MCP עם transport=http, path=/mcp
CMD ["python", "main.py"]
