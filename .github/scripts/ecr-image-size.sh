#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0 <image-ref> [platform]" >&2
  exit 1
}

[[ $# -ge 1 && $# -le 2 ]] || usage

image=$1
platform=${2:-linux/arm64}
os="${platform%%/*}"
arch="${platform#*/}"

manifest_json=$(docker buildx imagetools inspect "$image" --format '{{json .Manifest}}')

digest=$(
  echo "$manifest_json" | jq -r --arg os "$os" --arg arch "$arch" '
    if .layers then empty
    else .manifests[]? | select(.platform.os == $os and .platform.architecture == $arch) | .digest
    end
  '
)

if [[ -n "$digest" ]]; then
  raw_manifest=$(docker buildx imagetools inspect "${image}@${digest}" --raw)
else
  raw_manifest=$(docker buildx imagetools inspect "$image" --raw)
fi

echo "$raw_manifest" | jq '[.layers[]?.size, .config.size // 0] | add // 0'
