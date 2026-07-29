# Shared Terraform image pin helpers.
# Version/digest are pinned in docker/code-checks/Dockerfile and
# docker/infrastructure/Dockerfile.tests (keep those in sync).

.PHONY: check-terraform-version

# Full image reference including digest, e.g. hashicorp/terraform:1.15.8@sha256:...
TERRAFORM_IMAGE := $(shell sed -nE 's/^FROM[[:space:]]+(hashicorp\/terraform:[^[:space:]]+).*/\1/p' docker/code-checks/Dockerfile | head -1)

check-terraform-version: ## Verify required_version matches the pinned Terraform image
	@tag="$$(printf '%s\n' '$(TERRAFORM_IMAGE)' | sed -nE 's|^hashicorp/terraform:([^@]+).*|\1|p')"; \
	if [ -z "$$tag" ]; then \
		echo "Error: could not parse hashicorp/terraform tag from docker/code-checks/Dockerfile" >&2; \
		exit 1; \
	fi; \
	major_minor="$$(printf '%s\n' "$$tag" | cut -d. -f1,2)"; \
	expected="~> $${major_minor}.0"; \
	echo "Pinned Terraform image tag: $$tag (expect required_version = \"$$expected\")"; \
	status=0; \
	for file in $$(find infrastructure -name '*.tf' -print | sort); do \
		actual="$$(sed -nE 's/^[[:space:]]*required_version[[:space:]]*=[[:space:]]*\"([^\"]+)\".*/\1/p' "$$file" | head -1)"; \
		if [ -z "$$actual" ]; then \
			continue; \
		fi; \
		if [ "$$actual" != "$$expected" ]; then \
			echo "Error: $$file has required_version = \"$$actual\" (expected \"$$expected\")" >&2; \
			status=1; \
		fi; \
	done; \
	if [ "$$status" -ne 0 ]; then \
		exit "$$status"; \
	fi; \
	echo "All Terraform required_version constraints match $$expected"
