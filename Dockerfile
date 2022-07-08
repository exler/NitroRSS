FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1  
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \  
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt \  
    && rm -rf /tmp/requirements.txt \  
    && useradd -U skarlet \  
    && install -d -m 0755 -o skarlet -g skarlet /app/staticfiles

WORKDIR /app
USER skarlet:skarlet
COPY --chown=skarlet:skarlet . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]

CMD [ "server" ]
