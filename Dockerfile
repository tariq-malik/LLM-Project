FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && apt-get update && \
    apt-get install -y graphviz && which dot || (echo "ERROR: 'dot' executable not found after installation!" && exit 1)

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]