# Phase 2 Plan: Parallel Trivy Vulnerability Scanning

## Objective

Scan Docker images from ECR URIs using Trivy with parallel threading and store results in organized output folders.

## Scope

- Read `data/images.json` for image URIs.
- Run Trivy scans concurrently using ThreadPoolExecutor (max 3 workers).
- Save JSON reports in `output/` directory, segregated by repository.
- Handle scan failures gracefully and log progress.
- No dashboard or parsing in this phase.

## Inputs

- `data/images.json`: Contains image entries with `image_uri` and `repository`.
- Trivy CLI installed and available in PATH.
- Optional: `--max-workers` to adjust concurrency.

## Output

- `output/` directory with subfolders by repository.
- Each scan result saved as `<safe_image_uri>.json` in the repository subfolder.
- Example: `output/my-repo/nginx_latest.json`

## Implementation Steps

1. Check if Docker daemon is running; start Docker Desktop automatically if not (macOS only).
2. Load image entries from `data/images.json`.
3. Create `output/` directory structure.
4. Use ThreadPoolExecutor to scan images concurrently.
5. For each image, run `trivy image --cache-dir <unique_temp_dir> --format json --output <path> <image_uri>` (unique cache directory per scan to avoid conflicts).
6. Segregate output files by repository name.
7. Log success/failure for each scan.

### Run command

```bash
python3 src/scan_images.py --max-workers 3
```

## Validation

- Verify `output/` contains subfolders with JSON files.
- Check that scan results contain Trivy JSON structure.
- Confirm concurrency works (multiple scans running simultaneously).
- Ensure failed scans are logged but don't stop the process.

## Notes

- Assumes Trivy is installed.
- Segregation by repository helps with large numbers of images.
- Timeout per scan: 600 seconds.
- No external dependencies beyond standard library.