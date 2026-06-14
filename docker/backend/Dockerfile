ARG OWASP_GID=1000
ARG OWASP_UID=1000

# Shared builder setup for Production/Staging (builder-backend) and video (builder-video) images.
FROM python:3.13.14-alpine3.23@sha256:b0513989fa9be54569cac73f48a60320b74bb0f9ffa886568eea7e48a2432c04 AS builder-base

ARG OWASP_GID
ARG OWASP_UID

ENV APK_CACHE_DIR="/home/owasp/.cache/apk" \
    APK_SYMLINK_DIR="/etc/apk/cache" \
    OWASP_GID=${OWASP_GID} \
    OWASP_UID=${OWASP_UID} \
    PIP_CACHE_DIR="/home/owasp/.cache/pip" \
    POETRY_CACHE_DIR="/home/owasp/.cache/pypoetry" \
    PYTHONUNBUFFERED=1

RUN mkdir -p ${APK_CACHE_DIR} ${POETRY_CACHE_DIR} && \
    ln -fns ${APK_CACHE_DIR} ${APK_SYMLINK_DIR}

RUN --mount=type=cache,target=${APK_CACHE_DIR} \
    apk --no-cache update && \
    apk --no-cache upgrade && \
    addgroup -S -g ${OWASP_GID} owasp && \
    adduser -S -h /home/owasp -u ${OWASP_UID} -G owasp owasp && \
    chown -R owasp:owasp /home/owasp

COPY --chmod=444 --chown=root:root requirements/build.txt /tmp/
RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    python -m pip install --require-hashes --requirement /tmp/build.txt

WORKDIR /home/owasp

USER owasp

COPY --chmod=444 --chown=root:root poetry.lock poetry.toml pyproject.toml ./

# Production/Staging backend image (Poetry main dependency group only).
FROM builder-base AS builder-backend

ARG OWASP_GID
ARG OWASP_UID

RUN --mount=type=cache,target=${POETRY_CACHE_DIR},uid=${OWASP_UID},gid=${OWASP_GID} \
    poetry install --no-root --verbose --only main

# Less likely to cause cache invalidation items go first.
COPY entrypoint.sh manage.py wsgi.py Makefile ./
COPY scripts scripts
COPY settings settings
COPY templates templates
COPY static static
COPY apps apps

# Required to run make targets.
RUN ln -s . backend

RUN find /home/owasp/.venv -depth -type d -name __pycache__ -exec rm -rf {} + && \
    find /home/owasp/.venv -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete && \
    (find /home/owasp/.venv -depth -type d -name tests -exec rm -rf {} + 2>/dev/null || true)

# Runtime for Production/Staging backend.
FROM python:3.13.14-alpine3.23@sha256:b0513989fa9be54569cac73f48a60320b74bb0f9ffa886568eea7e48a2432c04 AS backend

ARG OWASP_GID
ARG OWASP_UID

RUN apk --no-cache update && \
    apk --no-cache upgrade && \
    apk --no-cache add make postgresql16-client=16.14-r0 && \
    rm -rf /var/cache/apk/* /var/tmp/* /tmp/* && \
    addgroup -S -g ${OWASP_GID} owasp && \
    adduser -S -h /home/owasp -u ${OWASP_UID} -G owasp owasp

ENV FORCE_COLOR=1 \
    PATH="/home/owasp/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

COPY --from=builder-backend --chmod=555 --chown=root:root /home/owasp /home/owasp
RUN rm -rf /home/owasp/.cache && \
    rm -rf /home/owasp/.local && \
    rm -rf /var/cache/apk/* /var/tmp/* /tmp/* && \
    chmod +x /home/owasp/entrypoint.sh

USER owasp

# Optional video image for community snapshot video generation.
FROM builder-base AS builder-video

ARG OWASP_GID
ARG OWASP_UID

RUN --mount=type=cache,target=${POETRY_CACHE_DIR},uid=${OWASP_UID},gid=${OWASP_GID} \
    poetry install --no-root --verbose --only main --only video

COPY entrypoint.sh manage.py wsgi.py Makefile ./
COPY scripts scripts
COPY settings settings
COPY templates templates
COPY static static
COPY apps apps

RUN ln -s . backend

RUN find /home/owasp/.venv -depth -type d -name __pycache__ -exec rm -rf {} + && \
    find /home/owasp/.venv -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete && \
    (find /home/owasp/.venv -depth -type d -name tests -exec rm -rf {} + 2>/dev/null || true)

# Runtime for video generation: ffmpeg for encoding and WeasyPrint libs for slide rendering.
FROM python:3.13.14-alpine3.23@sha256:b0513989fa9be54569cac73f48a60320b74bb0f9ffa886568eea7e48a2432c04 AS video

ARG OWASP_GID
ARG OWASP_UID

RUN apk --no-cache update && \
    apk --no-cache upgrade && \
    apk --no-cache add ffmpeg make postgresql16-client=16.14-r0 \
    # WeasyPrint dependencies: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
    so:libfontconfig.so.1 so:libgobject-2.0.so.0 so:libharfbuzz-subset.so.0 \
    so:libharfbuzz.so.0 so:libpango-1.0.so.0 so:libpangoft2-1.0.so.0 ttf-freefont && \
    rm -rf /var/cache/apk/* /var/tmp/* /tmp/* && \
    addgroup -S -g ${OWASP_GID} owasp && \
    adduser -S -h /home/owasp -u ${OWASP_UID} -G owasp owasp

ENV FORCE_COLOR=1 \
    PATH="/home/owasp/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /home/owasp

COPY --from=builder-video --chmod=555 --chown=root:root /home/owasp /home/owasp
RUN rm -rf /home/owasp/.cache && \
    rm -rf /home/owasp/.local && \
    rm -rf /var/cache/apk/* /var/tmp/* /tmp/* && \
    chmod +x /home/owasp/entrypoint.sh

USER owasp
