# Python build container
FROM python:3.10-slim as python-build
WORKDIR /app
ENV PIPENV_VENV_IN_PROJECT 1
COPY Pipfile.lock .
RUN apt-get update && \
    apt-get -y install build-essential mime-support && \
    pip install --upgrade pip && \
    pip install pipenv virtualenv && \
    pipenv requirements > requirements.txt && \
    virtualenv .venv && \
    ./.venv/bin/pip install -r requirements.txt

# Final container
FROM python:3.10-slim
WORKDIR /app

# Install mime support
COPY --from=python-build /etc/mime.types /etc/mime.types

# Expose ports
EXPOSE 9090

# Copy local files
COPY . .

# Copy virtual env
COPY --from=python-build /app/.venv ./.venv

# Collect static files
RUN ./.venv/bin/python manage.py collectstatic

# Run start script
CMD ["./run.sh"]
