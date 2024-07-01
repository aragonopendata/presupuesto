FROM python:2.7-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install the required packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
RUN chmod +x /app/entrypoint.sh

RUN useradd -ms /bin/bash django
USER django

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn","--workers=2","-b", "0.0.0.0:8000","project.wsgi:application"]
