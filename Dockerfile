FROM python:3.10-slim

WORKDIR /app

COPY . /app

#  ffmpeg
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bash.py"]
