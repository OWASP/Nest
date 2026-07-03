# Runtime secrets LocalStack fixture

This fixture tests the runtime-secrets migration without creating a complete Nest environment. It requires an already-running LocalStack instance plus `tflocal`, `awslocal`, AWS CLI, and `jq`.

Run it from the repository root:

```bash
bash infrastructure/localstack/test.sh
```

The test applies `prepare`, confirms legacy secret-valued SSM parameters and new Secrets Manager containers coexist, populates external secrets with fake values, and runs the deployment preflight. It then applies `complete` to the same state and verifies that secret-valued SSM parameters disappear while non-secret parameters remain. Finally, it inspects ECS `valueFrom` references and the execution-role IAM policy before destroying the fixture.

The script does not start LocalStack or manage its authentication token.