FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget unzip gnupg curl     chromium chromium-driver

ENV PATH="/usr/lib/chromium/:$PATH"

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
