FROM gcr.io/oss-fuzz-base/base-builder-python:v1@sha256:21f6fab17ace4dc76e1c56de91ee95d3d03da021df94b41056ba036f6c6f55e9

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY backend/requirements/cluster-fuzz-lite.txt /tmp/cluster-fuzz-lite.txt
RUN python -m pip install --no-cache-dir --only-binary :all: --require-hashes -r /tmp/cluster-fuzz-lite.txt

COPY .clusterfuzzlite/seed_corpora $SRC/seed_corpora

COPY backend/src/apps/__init__.py $SRC/apps/__init__.py
COPY backend/src/apps/common/search $SRC/apps/common/search
COPY backend/src/apps/slack/__init__.py $SRC/apps/slack/__init__.py
COPY backend/src/apps/slack/common/text.py $SRC/apps/slack/common/text.py
COPY backend/tests/cluster-fuzz-lite/apps $SRC/tests/cluster-fuzz-lite/apps
COPY --chmod=755 .clusterfuzzlite/build.sh $SRC/build.sh

WORKDIR $SRC
