# Usage

PhenoFetch provides a straightforward command-line interface for downloading and analyzing PhenoCam data. This page covers the basic usage patterns and common workflows.

## Command Structure

All PhenoFetch commands follow this basic structure:

```bash
phenofetch [command] [options]
```

The main commands are:

- `sites` - List all available PhenoCam sites
- `stats` - Display statistics for a site
- `estimate` - Estimate download size for a date range
- `download` - Download data for a specific site and date range

## Getting Help

To see all available commands and options:

```bash
phenofetch --help
```

For help with a specific command:

```bash
phenofetch [command] --help
```

## Common Arguments

Many commands share common arguments:

- `--site` - NEON site code (e.g., ABBY, BART)
- `--product` - NEON product ID (e.g., DP1.00033)
- `--start-date` - Start date in YYYY-MM-DD format
- `--end-date` - End date in YYYY-MM-DD format

## Basic Workflow

A typical workflow with PhenoFetch might look like this:

1. **Discover available sites**:
   ```bash
   phenofetch sites
   ```

2. **Check site statistics** to understand data availability:
   ```bash
   phenofetch stats --site HARV --product DP1.00033
   ```

3. **Estimate download size** before committing to a large download:
   ```bash
   phenofetch estimate --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
   ```

4. **Download the data**:
   ```bash
   phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download --output-dir ./my_phenocam_data
   ```

## Understanding Download Output

When downloading data, PhenoFetch will create a directory structure that preserves the organization of the files:

```
output_dir/
├── full_res/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── thumbnails/
│   ├── thumb1.jpg
│   ├── thumb2.jpg
│   └── ...
└── meta/
    ├── metadata1.meta
    ├── metadata2.meta
    └── ...
```

- `full_res/` - Contains full-resolution images
- `thumbnails/` - Contains thumbnail images
- `meta/` - Contains metadata files

## Managing Downloads

PhenoFetch provides several options to manage downloads effectively:

- **Batch size**: Control how many files are processed in each batch
  ```bash
  --batch-size 100
  ```

- **Concurrency**: Set maximum number of concurrent downloads (by default, this is auto-determined based on your system resources)
  ```bash
  --concurrency 8
  ```

- **Timeout**: Set connection timeout in seconds
  ```bash
  --timeout 60
  ```

## Preview Mode

To see what files would be downloaded without actually downloading them:

```bash
phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
```

Note that omitting the `--download` flag will only show a summary of available files.
