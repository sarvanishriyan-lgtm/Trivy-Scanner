# Phase 1 Plan: ECR Image Discovery

## Objective

Collect all Docker image URIs from Amazon ECR and store them in a JSON file for later scanning.

## Scope

- Discover all AWS ECR repositories accessible by the configured AWS CLI identity.
- List tagged images in each repository.
- Build a JSON file containing `repository`, `tag`, and `image_uri`.
- Keep the output in `data/images.json`.

## Inputs

The discovery step depends on AWS CLI configuration and optional runtime settings.

- AWS CLI credentials and configuration
  - `AWS_PROFILE` (optional)
  - `AWS_REGION` (optional)
- Existing AWS permissions to call ECR APIs:
  - `ecr:DescribeRepositories`
  - `ecr:DescribeImages`
- Optional CLI/ENV inputs for filtering or pagination if needed in the future.

## Output

- `images.json`
  - Each entry contains:
    - `repository`: ECR repository name
    - `repository_name`: ECR repository name
    - `repository_uri`: base repository URI
    - `created_at`: repository creation timestamp
    - `tag_immutability`: image tag mutability setting (`TAG_MUTABLE` or `IMMUTABLE`)
    - `encryption_type`: image encryption type (for example, `AES256` or `KMS`)
    - `tag`: image tag
    - `image_uri`: full repository URI with tag
  - Example entry:
    ```json
    {
      "repository": "my-app",
      "repository_name": "my-app",
      "repository_uri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app",
      "created_at": "2026-04-07T12:34:56Z",
      "tag_immutability": "IMMUTABLE",
      "encryption_type": "AES256",
      "tag": "latest",
      "image_uri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest"
    }
    ```

## Implementation Steps

1. Confirm AWS CLI is installed and configured.
2. Use `aws ecr describe-repositories` to enumerate repositories.
3. For each repository, use `aws ecr describe-images --repository-name <name> --filter tagStatus=TAGGED`.
4. Collect all image details and expand tagged image URIs.
5. Write the collected entries to `data/images.json`.
6. Use optional inputs `--profile` and `--region` to choose the AWS account and region.

### Run command

```bash
python3 src/fetch_ecr_images.py --profile <AWS_PROFILE> --region <AWS_REGION> --output data/images.json
```

## Validation

- Verify `data/images.json` exists after the script runs.
- Make sure each entry has a valid `image_uri`.
- Confirm there are no duplicate `image_uri` values unless the same image is intentionally repeated.
- Optionally run a quick spot-check by comparing a sample URI against ECR repository data.

## Notes

- This step does not perform vulnerability scanning.
- It only generates the list of images to scan in later phases.
- AWS CLI should already be configured with the correct SSO/profile before running this step.
