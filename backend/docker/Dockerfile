FROM python:3.13-slim AS builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --system owasp && \
    useradd --system --create-home --home-dir /home/owasp -g owasp owasp && \
    python -m pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

USER owasp

COPY --chown=owasp:owasp poetry.lock pyproject.toml ./
RUN poetry install --no-root --without dev --without test

COPY apps apps
COPY docker/entrypoint.sh entrypoint.sh
COPY manage.py wsgi.py ./
COPY settings settings
COPY static static
COPY templates templates

FROM python:3.13-slim

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --system owasp && \
    useradd --system --create-home --home-dir /home/owasp -g owasp owasp

ENV PATH="/home/owasp/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

COPY --from=builder --chown=owasp:owasp /home/owasp /home/owasp
RUN chmod +x /home/owasp/entrypoint.sh

USER owasp

CMD ["/home/owasp/entrypoint.sh"]
