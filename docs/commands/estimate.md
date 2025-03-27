# Estimate Command

The `estimate` command calculates the expected download size for PhenoCam data before committing to a full download.

## Description

This command helps you determine how much disk space will be required for downloading PhenoCam data for a specific site and date range. It retrieves all available file links for the specified criteria and checks the file sizes without downloading the actual content, providing a detailed breakdown of expected storage requirements.

## Usage

```bash
phenofetch estimate --site SITE_CODE --product PRODUCT_ID --start-date YYYY-MM-DD --end-date YYYY-MM-DD [options]
```

### Required Arguments

- `--site`: NEON site code (e.g., ABBY, BART)
- `--product`: NEON product ID (e.g., DP1.00033)
- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format

### Optional Arguments

- `--batch-size`: Number of files to process in each batch (default: 50)
- `--concurrency`: Maximum number of concurrent connections (default: auto-determined)
- `--timeout`: Connection timeout in seconds (default: 30)

## Output

The command generates two main tables:

1. **Data Summary**: Shows an overview of data availability within the date range, including:
   - Total days in the range
   - Days with available data
   - Number of full-resolution images
   - Number of thumbnails
   - Number of metadata files
   - Total number of files

2. **Size Estimate Summary**: Provides details on the estimated download size:
   - Size of full-resolution images
   - Size of thumbnails
   - Total size (with and without metadata)
   - Success and failure statistics

Example output:

```
Data Summary
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Metric           ┃ Value        ┃
┡━━━━━━━━━━━━━━━━━ ╇━━━━━━━━━━━━━━┩
│ Total days       │ 31           │
│ Days with data   │ 31           │
│ Total images     │ 558          │
│ Total thumbnails │ 558          │
│ Total metadata   │ 558          │
│ Total files      │ 1674         │
└──────────────────┴──────────────┘

Size Estimate Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Category                  ┃ Count ┃ Size         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ Full resolution images    │ 558   │ 1.45 GB      │
│ Thumbnails                │ 558   │ 42.24 MB     │
│ Metadata files            │ 558   │ size N/A     │
│ TOTAL (excluding metadata)│ 1116  │ 1.49 GB      │
│ Successfully checked      │ 1674  │              │
│ Failed                    │ 0     │              │
└───────────────────────────┴───────┴──────────────┘
```

## Notes

- The size estimation process does not download the actual files, only retrieves file size information.
- Metadata file sizes are typically small and may not be accurately reported by the server.
- The command automatically determines an optimal number of concurrent connections based on your system resources.
- Progress bars show the status of the estimation process.
- If errors occur during estimation, an additional table shows the types and counts of errors.

## Examples

Estimate download size for a one-month period:

```bash
phenofetch estimate --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
```

Use a larger batch size for faster estimation (but more memory usage):

```bash
phenofetch estimate --site HARV --product DP1.00033 --start-date 2023-01-01 --end-date 2023-03-31 --batch-size 100
```

Set a specific concurrency level:

```bash
phenofetch estimate --site BART --product DP1.00033 --start-date 2022-06-01 --end-date 2022-06-30 --concurrency 4
```

Increase the timeout for slow connections:

```bash
phenofetch estimate --site SOAP --product DP1.00033 --start-date 2023-01-01 --end-date 2023-02-28 --timeout 60
```

## Workflow

After estimating the download size, you can:

1. Decide if the storage space required is acceptable for your needs.
2. Adjust the date range if necessary to reduce the download size.
3. Proceed with downloading the data:
   ```bash
   phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download
   ```

## Troubleshooting

If the estimation fails or shows a high number of failures:

- Check your internet connection
- Try increasing the timeout value
- Reduce the batch size or concurrency for slower connections
- Try a smaller date range first
- Ensure the site code and date range contain available data (use the `stats` command to verify)
