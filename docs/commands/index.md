# Commands

PhenoFetch provides several commands to help you work with PhenoCam data. Each command serves a specific purpose in the data discovery and retrieval workflow.

## Available Commands

| Command | Description |
|---------|-------------|
| [`sites`](sites.md) | List all available PhenoCam sites |
| [`stats`](stats.md) | Display statistics for a specific PhenoCam site |
| [`estimate`](estimate.md) | Estimate download size for a date range |
| [`download`](download.md) | Download data for a specific site and date range |
| [`metadata`](metadata.md) | Process metadata files from downloaded PhenoCam data |

## Getting Help

You can get help for any command by adding the `--help` flag:

```bash
phenofetch [command] --help
```

## Command Structure

All PhenoFetch commands follow this basic structure:

```bash
phenofetch [command] [options]
```

## Global Options

Some options are available across multiple commands:

- `--site` - NEON site code (e.g., ABBY, BART)
- `--product` - NEON product ID (e.g., DP1.00033)
- `--start-date` - Start date in YYYY-MM-DD format
- `--end-date` - End date in YYYY-MM-DD format

## Command Flow

The commands are designed to be used in a logical flow:

1. Use `sites` to discover available PhenoCam sites
2. Use `stats` to understand what data is available for a site
3. Use `estimate` to check how large a download would be
4. Use `download` to retrieve the data
5. Use `metadata` to process and analyze the downloaded metadata files

Each command page in this section provides detailed information on usage, options, and examples.
