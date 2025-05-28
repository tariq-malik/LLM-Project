FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && apt-get update -y && apt-get install -y graphviz && which dot || (echo "ERROR: 'dot' executable not found after installation!" && exit 1)

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "python main.py && python -m http.server 8000"]