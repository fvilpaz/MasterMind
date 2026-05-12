FROM python:3.11-slim

WORKDIR /app

COPY trainer/web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "trainer/web/app.py"]
