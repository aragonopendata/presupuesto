FROM python:2.7-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Redirige a archive.debian.org y desactiva las verificaciones de fecha
RUN sed -i 's|deb.debian.org/debian|archive.debian.org/debian|g' /etc/apt/sources.list \
    && sed -i 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && printf 'Acquire::Check-Valid-Until "false";\nAcquire::AllowInsecureRepositories "true";\n' \
         > /etc/apt/apt.conf.d/99archive

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN groupadd -g 1234 django && \
    useradd -m -u 1234 -g django django

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app

RUN chmod +x /app/entrypoint.sh && chown django:django /app/theme-aragon/data
RUN mkdir /var/cache/django && chown -R django:django /var/cache/django
RUN mkdir -p /app/logs && chmod -R 775 /app/logs && chown -R django:django /app/logs

USER django

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn","--workers","5","-b","0.0.0.0:8000","project.wsgi:application"]
