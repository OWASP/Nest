#!/bin/sh
set -eu

find infrastructure/bootstrap infrastructure/modules \
	-name tests \
	-type d \
	-not -path "*/.terraform/*" | \
while IFS= read -r test_dir; do
	module_dir="$(dirname "${test_dir}")"
	echo "Testing ${module_dir}..."
	export TF_DATA_DIR="/tmp/tfdata/${module_dir}"
	terraform -chdir="${module_dir}" init -backend=false -input=false && \
		terraform -chdir="${module_dir}" test || exit 1
done
