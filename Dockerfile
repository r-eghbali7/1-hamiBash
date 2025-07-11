FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install wait-for-it

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]