# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ./app/requirements.txt /app/

RUN pip3 install -r requirements.txt

COPY ./app/.streamlit /app/.streamlit
COPY ./app/resolve_secrets.py /app/
COPY ./app/entrypoint.sh /app/

RUN chmod +x /app/entrypoint.sh

COPY ./app/streamlit_app.py /app/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["/app/entrypoint.sh"]
