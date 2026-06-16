FROM gcr.io/oss-fuzz-base/base-builder-python:v1

COPY backend/requirements/fuzz.txt /tmp/fuzz.txt
RUN pip install --require-hashes -r /tmp/fuzz.txt

COPY backend $SRC/Nest/backend
COPY .clusterfuzzlite $SRC/Nest/.clusterfuzzlite
WORKDIR $SRC/Nest
COPY .clusterfuzzlite/build.sh $SRC/build.sh
