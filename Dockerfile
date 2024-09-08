FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py migrate

CMD ["gunicorn", "excelparsing.wsgi:application", "--bind", "0.0.0.0:5000"]




