FROM python:3.12-slim

WORKDIR /app

# התקנת התלויות הקיימות
RUN pip install --upgrade pip
RUN pip install fastmcp

# נתקין את הספריות מהפרויקט (אם יש requirements.txt או pyproject.toml)
COPY pyproject.toml .
RUN pip install .

EXPOSE 8080

CMD ["python", "main.py"]
