FROM gcr.io/oss-fuzz-base/base-builder-python:v1@sha256:53a670f691b0bd348aa9f97a512918611ed960132c0fc124a12c2bc49ddec20a

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY backend/requirements/cluster-fuzz-lite.txt /tmp/cluster-fuzz-lite.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/cluster-fuzz-lite.txt

COPY .clusterfuzzlite/seed_corpora $SRC/seed_corpora

COPY backend/apps/__init__.py $SRC/apps/__init__.py
COPY backend/apps/common/search $SRC/apps/common/search
COPY backend/apps/slack/__init__.py $SRC/apps/slack/__init__.py
COPY backend/apps/slack/common/text.py $SRC/apps/slack/common/text.py
COPY backend/tests/cluster-fuzz-lite/apps $SRC/tests/cluster-fuzz-lite/apps
COPY --chmod=755 .clusterfuzzlite/build.sh $SRC/build.sh

WORKDIR $SRC
