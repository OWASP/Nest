#!/bin/sh
set -eu

test_dirs=$(find infrastructure/bootstrap infrastructure/modules \
	-name tests \
	-type d \
	-not -path "*/.terraform/*")

for test_dir in ${test_dirs}; do
	module_dir="$(dirname "${test_dir}")"
	echo "Testing ${module_dir}..."
	export TF_DATA_DIR="/tmp/tfdata/${module_dir}"
	terraform -chdir="${module_dir}" init -backend=false -input=false && \
		terraform -chdir="${module_dir}" test
done
