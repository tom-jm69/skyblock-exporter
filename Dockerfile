FROM python:3.13-alpine

# Copy requirements file

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests aiohttp

CMD ["python3", "-u", "main.py"]
