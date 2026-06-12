set -euo pipefail

usage() {
  echo "Usage: $0 sign|verify <account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>" >&2
  exit 1
}

[[ $# -eq 2 ]] || usage

command=$1
image=$2

case "$command" in
  sign | verify) ;;
  *) usage ;;
esac

repo="${image%:*}"
tag="${image##*:}"
repo_name="${repo#*.amazonaws.com/}"

if [[ "$repo" == "$image" || -z "$tag" || -z "$repo_name" ]]; then
  echo "::error::Invalid ECR image reference: ${image}" >&2
  exit 1
fi

digest=$(
  aws ecr batch-get-image \
    --repository-name "$repo_name" \
    --image-ids "imageTag=${tag}" \
    --query 'images[0].imageId.imageDigest' \
    --output text
)

if [[ -z "$digest" || "$digest" == "None" ]]; then
  echo "::error::Image not found in ECR: ${image} (repository: ${repo_name}, tag: ${tag})" >&2
  exit 1
fi

image_by_digest="${repo}@${digest}"
echo "Using image digest reference: ${image_by_digest}"

case "$command" in
  sign)
    cosign sign --yes "$image_by_digest"
    cosign verify "$image_by_digest"
    ;;
  verify)
    cosign verify "$image_by_digest"
    ;;
esac
