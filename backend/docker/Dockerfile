FROM python:3.13.5-alpine AS builder

ENV APK_CACHE_DIR="/home/owasp/.cache/apk" \
    APK_SYMLINK_DIR="/etc/apk/cache" \
    OWASP_GID=1000 \
    OWASP_UID=1000 \
    PIP_CACHE_DIR="/home/owasp/.cache/pip" \
    POETRY_CACHE_DIR="/home/owasp/.cache/pypoetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1

RUN mkdir -p ${APK_CACHE_DIR} ${POETRY_CACHE_DIR} && \
    ln -fns ${APK_CACHE_DIR} ${APK_SYMLINK_DIR}

RUN --mount=type=cache,target=${APK_CACHE_DIR} \
    apk update && apk upgrade && \
    addgroup -S -g ${OWASP_GID} owasp && \
    adduser -S -h /home/owasp -u ${OWASP_UID} -G owasp owasp && \
    chown -R owasp:owasp /home/owasp

RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    python -m pip install poetry --cache-dir ${PIP_CACHE_DIR}

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

FROM python:3.13.5-alpine

RUN apk update && \
    addgroup -S owasp && \
    adduser -S -h /home/owasp -G owasp owasp

ENV FORCE_COLOR=1 \
    PATH="/home/owasp/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

COPY --from=builder --chmod=555 --chown=owasp:owasp /home/owasp /home/owasp
RUN rm -rf /home/owasp/.cache && \
    rm -rf /home/owasp/.local && \
    chmod +x /home/owasp/entrypoint.sh

USER owasp

CMD ["/home/owasp/entrypoint.sh"]
