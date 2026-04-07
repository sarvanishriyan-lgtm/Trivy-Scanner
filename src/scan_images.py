import argparse
import concurrent.futures
import json
import os
import platform
import re
import subprocess
import time

IMAGES_FILE = 'data/images.json'
OUTPUT_DIR = 'output'
MAX_WORKERS_DEFAULT = 3
SCAN_TIMEOUT = 600  # 10 minutes per scan


def check_docker_running():
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def start_docker():
    if platform.system() == 'Darwin':  # macOS
        print('Docker not running. Starting Docker Desktop...')
        try:
            subprocess.run(['open', '-a', 'Docker'], check=True)
            print('Docker Desktop launched. Waiting for daemon to start...')
            # Wait up to 60 seconds for Docker to be ready
            for i in range(60):
                if check_docker_running():
                    print('Docker daemon is now running.')
                    return True
                time.sleep(1)
            print('Docker daemon did not start within 60 seconds.')
            return False
        except subprocess.CalledProcessError:
            print('Failed to launch Docker Desktop.')
            return False
    else:
        print('Automatic Docker startup not supported on this platform.')
        return False


def ensure_docker_running():
    if not check_docker_running():
        if not start_docker():
            print('Please start Docker manually and try again.')
            return False
    return True


def safe_filename(image_uri):
    sanitized = re.sub(r'[^A-Za-z0-9._-]+', '_', image_uri)
    return sanitized.strip('_')


def load_images():
    if not os.path.exists(IMAGES_FILE):
        raise FileNotFoundError(f'{IMAGES_FILE} not found. Run Phase 1 first.')

    with open(IMAGES_FILE, 'r') as f:
        images = json.load(f)

    return [entry for entry in images if entry.get('image_uri')]


def scan_image(entry):
    image_uri = entry.get('image_uri')
    repository = entry.get('repository', 'unknown')
    repo_dir = os.path.join(OUTPUT_DIR, repository)
    os.makedirs(repo_dir, exist_ok=True)

    filename = f'{safe_filename(image_uri)}.json'
    output_file = os.path.join(repo_dir, filename)

    # Use unique cache directory to avoid conflicts
    import tempfile
    cache_dir = tempfile.mkdtemp(prefix='trivy_cache_')

    print(f'Starting scan for {image_uri}')
    try:
        result = subprocess.run(
            ['trivy', 'image', '--cache-dir', cache_dir, '--format', 'json', '--output', output_file, image_uri],
            capture_output=True,
            text=True,
            timeout=SCAN_TIMEOUT,
        )
    except FileNotFoundError:
        return {'image_uri': image_uri, 'status': 'trivy_not_found', 'error': 'Trivy CLI not found.'}
    except subprocess.TimeoutExpired:
        return {'image_uri': image_uri, 'status': 'timeout', 'error': 'Scan timed out.'}
    finally:
        # Clean up temporary cache directory
        try:
            import shutil
            shutil.rmtree(cache_dir, ignore_errors=True)
        except:
            pass

    if result.returncode != 0:
        error_payload = {
            'image_uri': image_uri,
            'status': 'failed',
            'error': result.stderr.strip() or 'Unknown error',
        }
        try:
            with open(output_file, 'w') as f:
                json.dump({'scan_error': result.stderr.strip()}, f, indent=2)
        except OSError:
            pass

        return error_payload

    return {'image_uri': image_uri, 'status': 'success', 'output_file': output_file}


def scan_images(max_workers=MAX_WORKERS_DEFAULT):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    images = load_images()

    if not images:
        print('No images found in data/images.json.')
        return

    print(f'Queued {len(images)} images for scanning with up to {max_workers} concurrent workers.')

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {
            executor.submit(scan_image, entry): entry.get('image_uri') for entry in images
        }

        for future in concurrent.futures.as_completed(future_to_image):
            image_uri = future_to_image[future]
            try:
                result = future.result()
                results.append(result)
                status = result.get('status')
                if status == 'success':
                    print(f'Completed scan for {image_uri}')
                else:
                    print(f'Failed scan for {image_uri}: {result.get("error")}')
            except Exception as exc:
                print(f'Unhandled exception scanning {image_uri}: {exc}')

    success_count = sum(1 for r in results if r.get('status') == 'success')
    failure_count = len(results) - success_count
    print(f'Scanning complete: {success_count} succeeded, {failure_count} failed.')


def parse_args():
    parser = argparse.ArgumentParser(description='Scan ECR images with Trivy in parallel.')
    parser.add_argument('--max-workers', '-w', type=int, default=MAX_WORKERS_DEFAULT,
                        help='Maximum number of concurrent scans')
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        if not ensure_docker_running():
            return 1
        scan_images(max_workers=args.max_workers)
    except RuntimeError as exc:
        print(f'Error: {exc}')
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())