# Metadata Command

The `metadata` command processes PhenoCam metadata files and extracts key information into structured formats for analysis.

## Description

This command parses metadata files (`.meta`) downloaded with PhenoFetch and extracts important fields into a structured format like CSV, JSON, or Parquet. It's designed to make analyzing metadata across multiple images easier by consolidating the information into a single file.

The command can process either a single metadata file or an entire directory of files, extracting key fields like timestamp information, camera settings, and environmental data.

## Usage

```bash
phenofetch metadata --input-dir INPUT_PATH [options]
```

### Required Arguments

- `--input-dir`: Path to a directory containing metadata files or a single metadata file

### Optional Arguments

- `--output-meta`: Path where the output file should be saved (default: "extracted_metadata.csv")
- `--format`: Output format to use ("csv", "json", "parquet", or "all") (default: determined from output path extension)
- `--pattern`: File pattern to match when processing directories (default: ".meta")

## Output

The command extracts the following information from metadata files:

- **Filename Components**:
  - Provider (NEON)
  - Domain code
  - Site code
  - Product code
  - Date and time information
  - Day of year and day of week

- **Selected Metadata Fields**:
  - Camera temperature
  - Exposure settings
  - Network information
  - Other critical parameters

Output is saved in the specified format (CSV, JSON, Parquet, or all three) with one row per processed metadata file.

## Notes

- Files are processed in batches to optimize performance with large datasets
- When processing a directory, only files matching the specified pattern (default: ".meta") are processed
- The default output format is CSV if not specified

## Examples

Process all metadata files in a directory and save as CSV:

```bash
phenofetch metadata --input-dir ./phenocam_data/meta
```

Process files and specify an output file path:

```bash
phenofetch metadata --input-dir ./phenocam_data/meta --output-meta ./analysis/metadata_summary
```

Export in JSON format:

```bash
phenofetch metadata --input-dir ./phenocam_data/meta --format json --output-meta metadata_summary
```

Export in all available formats:

```bash
phenofetch metadata --input-dir ./phenocam_data/meta --format all --output-meta metadata_summary
```

Process only files with a specific pattern:

```bash
phenofetch metadata --input-dir ./phenocam_data/meta --pattern "HARV*.meta"
```

## Workflow

A typical workflow involving the metadata command might look like:

1. Download PhenoCam data for a site:
   ```bash
   phenofetch download --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30 --download
   ```

2. Process the metadata from the downloaded files:
   ```bash
   phenofetch metadata --input-dir ./phenocam_data/meta --format csv
   ```

3. Use the resulting CSV file for analysis in Python, R, or other tools

## Troubleshooting

If the command encounters issues:

- Ensure the input directory contains valid metadata files with the `.meta` extension
- Check that the output path is writable
- For JSON output, ensure there's sufficient disk space as JSON files can be larger than CSV
- If processing very large directories, consider breaking them into smaller batches or increasing system memory
