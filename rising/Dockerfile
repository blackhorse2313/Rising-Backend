FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt


ENV TESTING="False"
ENV SD_BASE_URL="http://host.docker.internal:7860"
ENV METEX_URL="http://34.203.75.157:8010"

CMD ["python","-u", "main.py"]