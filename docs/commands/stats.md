# Stats Command

The `stats` command provides detailed statistics about the available data for a specific PhenoCam site.

## Description

This command analyzes and displays comprehensive statistics about the available PhenoCam data for a specified site and product. It shows data availability by year and month, total image counts, and temporal distribution of images, helping you understand what data is available before downloading.

## Usage

```bash
phenofetch stats --site SITE_CODE --product PRODUCT_ID
```

### Required Arguments

- `--site`: NEON site code (e.g., ABBY, BART)
- `--product`: NEON product ID (e.g., DP1.00033)

## Output

The command generates two main tables:

1. **Summary Table**: Shows data availability by year and month, including:
   - Year
   - Month
   - Image Count
   - URL for the data

2. **Statistics Table**: Shows:
   - Total image count
   - Year-by-year image counts
   - Monthly average image counts

Example output:

```
Summary for NEON.D01.HARV.DP1.00033
┏━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Year ┃ Month ┃ Image Count ┃ URL                                                          ┃
┡━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2024 │ Mar   │ 3648        │ /webcam/browse/NEON.D01.HARV.DP1.00033/2024/03/              │
│ 2024 │ Feb   │ 3371        │ /webcam/browse/NEON.D01.HARV.DP1.00033/2024/02/              │
│ 2024 │ Jan   │ 3658        │ /webcam/browse/NEON.D01.HARV.DP1.00033/2024/01/              │
│ 2023 │ Dec   │ 3621        │ /webcam/browse/NEON.D01.HARV.DP1.00033/2023/12/              │
│ ...  │ ...   │ ...         │ ...                                                          │
└──────┴───────┴─────────────┴──────────────────────────────────────────────────────────────┘

Total Images: 124,896

Images by Year
┏━━━━━━┳━━━━━━━━━━━━━┓
┃ Year ┃ Image Count ┃
┡━━━━━━╇━━━━━━━━━━━━━┩
│ 2024 │ 10677       │
│ 2023 │ 43157       │
│ 2022 │ 42291       │
│ 2021 │ 28771       │
└──────┴─────────────┘
```

## Notes

- The data is sorted in reverse chronological order, with the most recent months first.
- Missing months or years indicate that no data is available for those periods.
- The total image count gives you an idea of how much data is available for the site.
- Year totals help identify which years have the most data.
- Monthly averages can reveal seasonal patterns in data collection.

## Examples

Check statistics for Harvard Forest site:

```bash
phenofetch stats --site HARV --product DP1.00033
```

Check statistics for Abby Road site:

```bash
phenofetch stats --site ABBY --product DP1.00033
```

## Workflow

After examining the statistics for a site, you can:

1. Decide on a date range of interest based on data availability.
2. Estimate the download size for that range:
   ```bash
   phenofetch estimate --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30
   ```
3. Download the data for the chosen range:
   ```bash
   phenofetch download --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30 --download
   ```

## Troubleshooting

If the command fails, check that:

- The site code is valid (use `phenofetch sites` to see all valid site codes)
- The product ID is correct (typically DP1.00033 for PhenoCam data)
- You have an active internet connection
