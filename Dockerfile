FROM python:3.12-rc-slim

WORKDIR /app

COPY /app .

RUN pip install -r requirements.txt --no-cache-dir

CMD ["python", "."]