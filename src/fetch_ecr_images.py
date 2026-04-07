import argparse
import json
import os
import subprocess

DEFAULT_IMAGES_FILE = 'data/images.json'


def run_aws_command(args, profile=None, region=None):
    command = ['aws']
    if profile:
        command += ['--profile', profile]
    if region:
        command += ['--region', region]
    command += args + ['--output', 'json']

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except FileNotFoundError:
        raise RuntimeError('AWS CLI not found. Install and configure AWS CLI before running this script.')
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else 'No error output.'
        raise RuntimeError(f"AWS CLI command failed: {' '.join(command)}\n{stderr}")


def list_ecr_repositories(profile=None, region=None):
    repositories = []
    next_token = None

    while True:
        args = ['ecr', 'describe-repositories']
        if next_token:
            args += ['--next-token', next_token]

        data = run_aws_command(args, profile=profile, region=region)
        repositories.extend(data.get('repositories', []))
        next_token = data.get('nextToken')
        if not next_token:
            break

    return repositories


def list_repository_images(repository_name, profile=None, region=None):
    images = []
    next_token = None

    while True:
        args = [
            'ecr',
            'describe-images',
            '--repository-name',
            repository_name,
            '--filter',
            'tagStatus=TAGGED',
        ]
        if next_token:
            args += ['--next-token', next_token]

        data = run_aws_command(args, profile=profile, region=region)
        images.extend(data.get('imageDetails', []))
        next_token = data.get('nextToken')
        if not next_token:
            break

    return images


def collect_images(profile=None, region=None):
    image_entries = []
    repositories = list_ecr_repositories(profile=profile, region=region)

    for repository in repositories:
        repository_name = repository.get('repositoryName')
        repository_uri = repository.get('repositoryUri')
        created_at = repository.get('createdAt')
        tag_immutability = repository.get('imageTagMutability')
        encryption_type = repository.get('encryptionConfiguration', {}).get('encryptionType')

        if not repository_name or not repository_uri:
            continue

        image_details = list_repository_images(repository_name, profile=profile, region=region)
        for image in image_details:
            tags = image.get('imageTags') or []
            for tag in tags:
                image_entries.append({
                    'repository': repository_name,
                    'repository_name': repository_name,
                    'repository_uri': repository_uri,
                    'created_at': created_at,
                    'tag_immutability': tag_immutability,
                    'encryption_type': encryption_type,
                    'tag': tag,
                    'image_uri': f'{repository_uri}:{tag}',
                })

    return image_entries


def save_images(image_entries, output_file=DEFAULT_IMAGES_FILE):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(image_entries, f, indent=2)

    print(f'Saved {len(image_entries)} image entries to {output_file}')


def parse_args():
    parser = argparse.ArgumentParser(description='Fetch ECR image metadata and write images.json.')
    parser.add_argument('--output', '-o', default=DEFAULT_IMAGES_FILE, help='Output JSON file path')
    parser.add_argument('--profile', '-p', help='AWS CLI profile name')
    parser.add_argument('--region', '-r', help='AWS region')
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        image_entries = collect_images(profile=args.profile, region=args.region)
        save_images(image_entries, output_file=args.output)
    except RuntimeError as exc:
        print(f'Error: {exc}')
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
