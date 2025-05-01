FROM python:3.13.3-alpine AS builder

RUN apk update && \
    addgroup -S owasp && \
    adduser -S -h /home/owasp -G owasp owasp && \
    python -m pip install poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

USER owasp

COPY --chmod=444 --chown=owasp:owasp poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pypotery \
    poetry install --no-root --without dev --without test

COPY apps apps
COPY docker/entrypoint.sh entrypoint.sh
COPY manage.py wsgi.py ./
COPY settings settings
COPY static static
COPY templates templates

FROM python:3.13.3-alpine

RUN apk update && \
    addgroup -S owasp && \
    adduser -S -h /home/owasp -G owasp owasp

ENV PATH="/home/owasp/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

COPY --from=builder --chmod=755 --chown=owasp:owasp /home/owasp/.venv /home/owasp/.venv
COPY --from=builder --chmod=555 --chown=owasp:owasp /home/owasp /home/owasp
RUN chmod +x /home/owasp/entrypoint.sh

USER owasp

CMD ["/home/owasp/entrypoint.sh"]
