# Download Command

The `download` command retrieves PhenoCam images and metadata for a specific site and date range.

## Description

This command allows you to download PhenoCam data (full-resolution images, thumbnails, and metadata files) for a specified site and date range. It supports concurrent downloading for improved performance and provides detailed progress information during the download process.

## Usage

```bash
phenofetch download --site SITE_CODE --product PRODUCT_ID --start-date YYYY-MM-DD --end-date YYYY-MM-DD [options]
```

### Required Arguments

- `--site`: NEON site code (e.g., ABBY, BART)
- `--product`: NEON product ID (e.g., DP1.00033)
- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format

### Optional Arguments

- `--download`: Flag to actually download files (if omitted, just shows a summary)
- `--output-dir`: Directory to save downloaded files (default: ./phenocam_data)
- `--batch-size`: Number of files to download in each batch (default: 50)
- `--concurrency`: Maximum number of concurrent downloads (default: auto-determined)
- `--timeout`: Connection timeout in seconds (default: 30)

## Output

When run without the `--download` flag, the command displays a summary of available files:

```
Summary:
Total days: 31
Days with data: 31
Total images: 558
Total thumbnails: 558
Total metadata files: 558
Total files: 1674
```

When run with the `--download` flag, it shows:

1. Configuration summary
2. Progress information during download
3. Batch completion updates
4. Final summary statistics

Example output during download:

```
PhenoFetch Configuration:
  Site code: ABBY
  Product ID: DP1.00033
  Date range: 2022-01-01 to 2022-01-31
  Download files: Yes
  Output directory: ./phenocam_data
  Batch size: 50
  Concurrency: Auto
  Timeout: 30 seconds

Fetching data for NEON.D16.ABBY.DP1.00033 from 2022-01-01 to 2022-01-31...

Summary:
Total days: 31
Days with data: 31
Total images: 558
Total thumbnails: 558
Total metadata files: 558
Total files: 1674

Starting download of 1674 files...

Overall progress: 100%|████████████████████████████| 1674/1674 [03:42<00:00, 7.52files/s]
Batch 34/34 complete: 50 successful, 0 failed

Download Complete!
Total files processed: 1674
Successfully downloaded: 1674
Already existed: 0
Failed: 0
```

## File Organization

Downloaded files are organized into three subdirectories:

- `full_res/`: Contains full-resolution images
- `thumbnails/`: Contains thumbnail images
- `meta/`: Contains metadata files

The original filenames are preserved.

## Notes

- If a file already exists in the output directory, it will be skipped (not re-downloaded).
- The command automatically determines an optimal number of concurrent downloads based on your system resources.
- Downloads are processed in batches to manage memory usage and provide better progress reporting.
- Small pauses between batches help prevent overwhelming the server.
- Failed downloads are tracked and reported at the end.

## Examples

Show summary without downloading:

```bash
phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
```

Download data to the default directory:

```bash
phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download
```

Download to a specific directory:

```bash
phenofetch download --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30 --download --output-dir ./harvard_data
```

Use a larger batch size for faster downloading:

```bash
phenofetch download --site BART --product DP1.00033 --start-date 2022-06-01 --end-date 2022-06-30 --download --batch-size 100
```

Set a specific concurrency level:

```bash
phenofetch download --site KONZ --product DP1.00033 --start-date 2023-01-01 --end-date 2023-01-15 --download --concurrency 4
```

Increase the timeout for slow connections:

```bash
phenofetch download --site SOAP --product DP1.00033 --start-date 2023-01-01 --end-date 2023-02-28 --download --timeout 60
```

## Workflow Recommendations

1. Before downloading a large dataset:
   - Use the `sites` command to find available sites
   - Use the `stats` command to check data availability
   - Use the `estimate` command to check download size

2. Start with a small date range to verify everything works correctly.

3. For large downloads, consider:
   - Increasing batch size for faster downloads (if you have sufficient memory)
   - Using the default auto-determined concurrency (or setting a lower value for slower connections)

## Troubleshooting

If downloads fail:

- Check your internet connection
- Try increasing the timeout value
- Reduce the batch size or concurrency for slower connections
- Try a smaller date range first
- Make sure the output directory is writable
- Check if the site has data for the specified date range (use the `stats` command)
