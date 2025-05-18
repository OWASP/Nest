FROM python:3.13.3-alpine AS builder

ENV OWASP_GID=1000 \
    OWASP_UID=1000 \
    POETRY_CACHE_DIR="/home/owasp/.cache/pypoetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1

RUN apk update && apk upgrade && \
    addgroup -S -g ${OWASP_GID} owasp && \
    adduser -S -h /home/owasp -u ${OWASP_UID} -G owasp owasp && \
    mkdir -p ${POETRY_CACHE_DIR} && \
    chown -R owasp:owasp /home/owasp && \
    python -m pip install poetry

WORKDIR /home/owasp

USER owasp

COPY --chmod=444 --chown=owasp:owasp poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=${POETRY_CACHE_DIR},uid=${OWASP_UID},gid=${OWASP_GID} \
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

COPY --from=builder --chmod=555 --chown=owasp:owasp /home/owasp /home/owasp
RUN rm -rf /home/owasp/.cache && \
    rm -rf /home/owasp/.local && \
    chmod +x /home/owasp/entrypoint.sh

USER owasp

CMD ["/home/owasp/entrypoint.sh"]
